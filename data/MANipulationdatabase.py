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
import boto3

load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

if not aws_access_key or not aws_secret_key:
    raise ValueError('Credentials AWS manquantes dans les variables d\'environnement')

client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
