#!/usr/bin/env python3
"""
devops_pipeline_watcher.py

Petit agent qui surveille les workflows GitHub Actions d'un repo, et quand
un run échoue, il va chercher les logs, demande à Claude d'analyser ce qui
a foiré, et envoie un résumé clair sur Slack avec une piste de correctif.

Idée de base : au lieu de devoir aller fouiller dans les logs GitHub Actions
à chaque échec de pipeline, on a direct un message Slack avec "voilà ce qui
a cassé, voilà probablement pourquoi".

Pré-requis (variables d'env, à mettre dans un .env ou dans les secrets du
serveur où tourne le script, JAMAIS en dur dans le code) :
    GITHUB_TOKEN       -> token avec accès "Actions: read" sur le repo
    ANTHROPIC_API_KEY  -> clé API Claude
    SLACK_WEBHOOK_URL  -> webhook du channel où on veut les alertes

Usage:
    python devops_pipeline_watcher.py --repo monorg/mon-repo --interval 60

Note perso: pour l'instant ça poll toutes les X secondes, ce qui n'est pas
super élégant (un webhook GitHub serait plus propre et instantané) mais ça
évite d'avoir à exposer un serveur public juste pour recevoir les events.
A migrer vers un webhook plus tard si le polling devient trop lourd.
"""

import os
import time
import json
import argparse
import logging
from datetime import datetime, timezone

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("pipeline_watcher")

GITHUB_API = "https://api.github.com"

# fichier tout simple pour se souvenir des runs déjà notifiés
# (pas de base de données pour un script aussi petit, ça suffit largement)
STATE_FILE = ".watcher_state.json"


def load_seen_runs():
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError):
        # fichier corrompu ou illisible, on repart de zéro plutôt que de planter
        log.warning("Impossible de lire %s, on repart avec un état vide", STATE_FILE)
        return set()


def save_seen_runs(seen_runs):
    # on garde que les 500 derniers ids pour pas que le fichier grossisse indéfiniment
    trimmed = list(seen_runs)[-500:]
    with open(STATE_FILE, "w") as f:
        json.dump(trimmed, f)


def get_failed_runs(repo, github_token):
    """Récupère les derniers workflow runs et retourne ceux qui ont échoué."""
    url = f"{GITHUB_API}/repos/{repo}/actions/runs"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    params = {"per_page": 20, "status": "completed"}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    runs = resp.json().get("workflow_runs", [])

    return [r for r in runs if r["conclusion"] == "failure"]


def get_run_logs_summary(repo, run_id, github_token):
    """
    Récupère les jobs du run et renvoie un texte avec les noms des steps
    qui ont échoué (on ne télécharge pas les logs complets, ça peut être
    énorme et c'est pas tout utile pour l'analyse).
    """
    url = f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}/jobs"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    jobs = resp.json().get("jobs", [])

    summary_lines = []
    for job in jobs:
        if job["conclusion"] != "failure":
            continue
        summary_lines.append(f"Job: {job['name']}")
        for step in job.get("steps", []):
            if step["conclusion"] == "failure":
                summary_lines.append(f"  -> étape en échec: {step['name']}")

    return "\n".join(summary_lines) if summary_lines else "Pas de détail de step disponible."


def ask_claude_for_diagnosis(run_info, logs_summary, anthropic_api_key):
    """Envoie le contexte du run à Claude et récupère une piste de diagnostic."""
    prompt = f"""Tu es un assistant DevOps. Un pipeline CI/CD vient d'échouer, voici le contexte :

Workflow: {run_info['name']}
Branche: {run_info['head_branch']}
Commit: {run_info['head_sha'][:8]}
URL: {run_info['html_url']}

Résumé des jobs/étapes en échec:
{logs_summary}

Donne en 3-4 phrases max : la cause probable de l'échec et une suggestion concrète
pour corriger. Reste direct, pas de blabla, c'est pour une alerte Slack."""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def send_slack_alert(webhook_url, run_info, diagnosis):
    message = {
        "text": (
            f":rotating_light: *Pipeline en échec* — {run_info['name']} "
            f"sur `{run_info['head_branch']}`\n\n"
            f"*Diagnostic IA :*\n{diagnosis}\n\n"
            f"<{run_info['html_url']}|Voir le run sur GitHub>"
        )
    }
    resp = requests.post(webhook_url, json=message, timeout=10)
    resp.raise_for_status()


def check_once(repo, github_token, anthropic_api_key, slack_webhook_url, seen_runs):
    failed_runs = get_failed_runs(repo, github_token)

    new_failures = [r for r in failed_runs if str(r["id"]) not in seen_runs]

    if not new_failures:
        log.info("Aucun nouvel échec détecté.")
        return

    for run in new_failures:
        log.info("Nouvel échec détecté: run #%s (%s)", run["id"], run["name"])

        try:
            logs_summary = get_run_logs_summary(repo, run["id"], github_token)
            diagnosis = ask_claude_for_diagnosis(run, logs_summary, anthropic_api_key)
            send_slack_alert(slack_webhook_url, run, diagnosis)
            log.info("Alerte envoyée sur Slack pour le run #%s", run["id"])
        except requests.RequestException as e:
            # on log l'erreur mais on continue, pas la peine de crasher tout le script
            # pour un run qu'on n'a pas réussi à traiter
            log.error("Erreur en traitant le run #%s: %s", run["id"], e)
            continue

        seen_runs.add(str(run["id"]))

    save_seen_runs(seen_runs)


def main():
    parser = argparse.ArgumentParser(description="Surveille un pipeline CI/CD GitHub Actions et alerte sur Slack en cas d'échec.")
    parser.add_argument("--repo", required=True, help="Repo au format org/nom-du-repo")
    parser.add_argument("--interval", type=int, default=60, help="Intervalle de polling en secondes (défaut: 60)")
    args = parser.parse_args()

    github_token = os.environ.get("GITHUB_TOKEN")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    missing = [
        name for name, val in [
            ("GITHUB_TOKEN", github_token),
            ("ANTHROPIC_API_KEY", anthropic_api_key),
            ("SLACK_WEBHOOK_URL", slack_webhook_url),
        ] if not val
    ]
    if missing:
        log.error("Variables d'environnement manquantes: %s", ", ".join(missing))
        return

    log.info("Surveillance du pipeline %s démarrée (polling toutes les %ss)", args.repo, args.interval)
    seen_runs = load_seen_runs()

    # boucle infinie tout bête, à lancer dans un service systemd ou un container
    # qui restart automatiquement si jamais ça plante
    while True:
        try:
            check_once(args.repo, github_token, anthropic_api_key, slack_webhook_url, seen_runs)
        except Exception as e:
            # filet de sécurité général, on veut pas que le watcher meure
            # silencieusement à cause d'une erreur réseau ponctuelle
            log.error("Erreur inattendue pendant le check: %s", e)

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
