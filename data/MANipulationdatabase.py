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
import boto3
import os
from botocore.exceptions import ClientError

# Option 1 : Variables d'environnement
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Option 2 : IAM Role (recommandé en production)
client = boto3.client('s3')

# Option 3 : Profil AWS CLI nommé
session = boto3.Session(profile_name='production')
client = session.client('s3')

# Vérifier que les credentials sont présents
if not access_key or not secret_key:
    raise ValueError('AWS credentials not found in environment variables')
