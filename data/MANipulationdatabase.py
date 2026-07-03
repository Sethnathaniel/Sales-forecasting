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

# Approche 1 : Variables d'environnement
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Approche 2 : Rôle IAM (recommandé en production)
client = boto3.client('s3')

# Approche 3 : Secrets Manager
def get_aws_credentials():
    secrets_client = boto3.client('secretsmanager')
    try:
        response = secrets_client.get_secret_value(SecretId='prod/aws/credentials')
        return response['SecretString']
    except ClientError as e:
        raise Exception(f'Erreur récupération secrets: {e}')
