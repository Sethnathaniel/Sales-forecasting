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
from botocore.exceptions import ClientError

# Approche 1 : Variables d'environnement
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Approche 2 : Utiliser le rôle IAM (recommandé)
client = boto3.client('s3')

# Approche 3 : Gestionnaire de secrets
import json
def get_aws_credentials():
    try:
        secrets_client = boto3.client('secretsmanager')
        secret = secrets_client.get_secret_value(SecretId='aws-credentials')
        return json.loads(secret['SecretString'])
    except ClientError as e:
        raise ValueError(f'Erreur lors de la récupération des credentials: {e}')
