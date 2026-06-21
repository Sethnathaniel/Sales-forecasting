"""
Application Flask intentionnellement vulnérable.
Sert UNIQUEMENT à tester un scanner SAST (SecMind). Ne jamais déployer.
"""

import os
import sqlite3
import subprocess
import pickle
import yaml
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- Vuln 1 : secret en dur (hardcoded credentials) ---
API_KEY = "sk-live-51HZx9KQ8d8f7sdf987sdfasdf"
DB_PASSWORD = "SuperSecretPassword123!"


# --- Vuln 2 : injection SQL (concatenation de string dans une requete) ---
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    return str(cursor.fetchall())


# --- Vuln 3 : XSS (rendu de template avec input utilisateur non échappé) ---
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    template = "<h1>Bonjour " + name + "</h1>"
    return render_template_string(template)


# --- Vuln 4 : injection de commande OS ---
@app.route("/ping")
def ping():
    host = request.args.get("host")
    result = subprocess.run("ping -c 1 " + host, shell=True, capture_output=True)
    return result.stdout


# --- Vuln 5 : désérialisation non sécurisée (pickle sur input utilisateur) ---
@app.route("/load", methods=["POST"])
def load_data():
    raw = request.get_data()
    obj = pickle.loads(raw)
    return str(obj)


# --- Vuln 6 : YAML non sécurisé (yaml.load sans Loader sûr) ---
@app.route("/config", methods=["POST"])
def load_config():
    raw = request.get_data()
    config = yaml.load(raw, Loader=yaml.Loader)
    return str(config)


# --- Vuln 7 : path traversal ---
@app.route("/download")
def download():
    filename = request.args.get("file")
    path = os.path.join("uploads", filename)
    with open(path, "rb") as f:
        return f.read()


# --- Vuln 8 : débogage activé en production ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
