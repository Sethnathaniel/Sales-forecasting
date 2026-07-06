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

# Les credentials sont chargés automatiquement par boto3 depuis:
# 1. Variables d'environnement AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY
# 2. Fichier ~/.aws/credentials
# 3. Rôle IAM (si exécuté sur EC2/Lambda)

try:
    # Pas de credentials en dur - boto3 les récupère automatiquement
    dynamodb = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    
    # Utilisation normale des services AWS
    table = dynamodb.Table('ma_table')
except ClientError as e:
    print(f'Erreur AWS: {e}')
    raise
