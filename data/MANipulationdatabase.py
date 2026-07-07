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
import boto3
from dotenv import load_dotenv

load_dotenv()

# Option 1 : Variables d'environnement
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Option 2 : Rôle IAM (recommandé en production)
client = boto3.client('s3')  # Utilise automatiquement les credentials du rôle IAM

# Option 3 : AWS Secrets Manager
import json
secrets_client = boto3.client('secretsmanager')
secret = json.loads(secrets_client.get_secret_value(SecretId='prod/aws-credentials')['SecretString'])
aws_access_key = secret['access_key']
aws_secret_key = secret['secret_key']
