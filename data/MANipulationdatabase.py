import sqlite3

def recuperer_utilisateur(user_output):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # ==============================================================================
    # ❌ TEXTE DE TEST VULNÉRABLE (Sera détecté par SecMind)a
    # ==============================================================================
    # Ce code est dangereux car il concatène directement l'entrée utilisateur avec "+"
    cursor.execute("SELECT * FROM kitchzen WHERE username = '" + user_output + "'")
    
    return cursor.fetchall()

# Simulation d'une clé API exposée pour faire réagir les autres filtres en même temps
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise ValueError('Les variables d\'environnement AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY doivent être définies')
