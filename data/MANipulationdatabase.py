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

# Récupération de la clé AWS depuis une variable d'environnement
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# Initialisation du client AWS avec les variables d'environnement
db_client = boto3.client(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
