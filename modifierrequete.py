#recuperation de données de requete(le code est dans systeme d'information), il faut lié avec sylob_api.py
import base64
import requests
import tkinter as tk
from tkinter import ttk
import json
import xmltodict  # pip install xmltodict

# ==========================
# Paramètres
# ==========================
identifiant = "609brjv18mdtie1ologvlb2ec1"
secret = "17e4up4k513lt8aa11066ekrpj2mjlnlc301m7leqo5fme9uts69"
unite_persistance = "SAP"
pool_url = "https://fornells-production-sap-cloud-prd.auth.eu-west-3.amazoncognito.com/oauth2/token"

# ==========================
# Encoder identifiant:secret en Base64
# ==========================
credentials = f"{identifiant}:{secret}"
base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
headers = {
    "Authorization": f"Basic {base64_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}

# ==========================
# Corps de la requête POST
# ==========================
post_data = {
    "grant_type": "client_credentials",
    "scope": f"ClientExterne/rest_write ERP/{unite_persistance}"
}

# ==========================
# Récupération du token
# ==========================
print("⏳ Obtention du token...")
response = requests.post(pool_url, headers=headers, data=post_data)

if response.status_code == 200:
    try:
        token_info = response.json()
        access_token = token_info.get("access_token")
        if not access_token:
            print("❌ Pas de token dans la réponse :", response.text)
            exit()
        print("✅ Token obtenu avec succès !")
    except ValueError:
        print("❌ La réponse n’est pas du JSON valide :", response.text)
        exit()
else:
    print("❌ Erreur lors de la récupération du token :", response.status_code)
    print(response.text)
    exit()

# ==========================
# Appel API Sylob avec le token
# ==========================
api_url = "https://fornells.syloberp.com/rest/query/00000381/resultat?structureDonnee=2"
api_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("\n⏳ Appel de l’API Sylob...")
api_response = requests.get(api_url, headers=api_headers)

if api_response.status_code != 200:
    print(f"❌ Erreur API Sylob : {api_response.status_code}")
    print(api_response.text)
    exit()

raw_text = api_response.text.strip()

# ==========================
# Détection du format de réponse
# ==========================
if raw_text.startswith("{") or raw_text.startswith("["):
    print("📦 Réponse au format JSON détectée.")
    try:
        json_data = api_response.json()
    except ValueError:
        print("❌ JSON invalide :", raw_text[:500])
        exit()
elif raw_text.startswith("<?xml") or raw_text.startswith("<"):
    print("📄 Réponse au format XML détectée.")
    try:
        xml_dict = xmltodict.parse(raw_text)
        json_data = json.loads(json.dumps(xml_dict))  # conversion en dict standard
    except Exception as e:
        print("❌ Erreur de parsing XML :", e)
        print(raw_text[:500])
        exit()
else:
    print("❌ Format de réponse inconnu :")
    print(raw_text[:500])
    exit()

print("✅ Données reçues et converties avec succès !")

# ==========================
# Fonction pour insérer dans Treeview
# ==========================
def insert_json(tree, parent, data):
    """Insère récursivement les données JSON/XML dans Treeview"""
    if isinstance(data, dict):
        for key, value in data.items():
            node = tree.insert(parent, "end", text=str(key), open=False)
            insert_json(tree, node, value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            node = tree.insert(parent, "end", text=f"[{index}]", open=False)
            insert_json(tree, node, item)
    else:
        tree.insert(parent, "end", text=str(data))

# ==========================
# Interface graphique Tkinter
# ==========================
root = tk.Tk()
root.title("API Sylob Viewer (JSON/XML)")
root.geometry("900x700")

frame = ttk.Frame(root)
frame.pack(expand=True, fill="both")

tree = ttk.Treeview(frame)
tree.pack(side="left", expand=True, fill="both")

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

insert_json(tree, "", json_data)

root.mainloop()
