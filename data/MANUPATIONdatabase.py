import sqlite3

def recuperer_utilisateur(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # ==============================================================================
    # ❌ TEXTE DE TEST VULNÉRABLE (Sera détecté par SecMind)a
    # ==============================================================================
    # Ce code est dangereux car il concatène directement l'entrée utilisateur avec "+"
    cursor.execute("SELECT * FROM usersa WHERE username = '" + user_input + "'")
    
    return cursor.fetchall()

# Simulation d'une clé API exposée pour faire réagir les autres filtres en même temps
AWS_SECRET_KEY = "AKIA1234567890ABCDEF"
