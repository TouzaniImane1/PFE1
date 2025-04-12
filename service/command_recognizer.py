from executors.command_executor import command_map

def recognize_command(text):
    """
    Associe directement un texte transcrit à une commande définie.
    """
    text = convert_to_number(text)  # Convertit les nombres écrits en chiffres
    text = text.lower().strip()

    # Vérifier si le texte correspond exactement à une commande
    if text in command_map:
        return text
    
    # Vérifier si le texte contient une partie clé d'une commande
    for command in command_map.keys():
        if command in text:
            return command
    return None
    
# Ajouter cette fonction tout en haut du fichier
NUMBERS = {
    "un": "1", "deux": "2", "trois": "3",
    "quatre": "4", "cinq": "5", "six": "6",
    "sept": "7", "huit": "8", "neuf": "9", "zéro": "0"
}

def convert_to_number(text):
    words = text.split()
    converted_words = [NUMBERS[word] if word in NUMBERS else word for word in words]
    return " ".join(converted_words)

    # Si aucune correspondance n'est trouvée, retourner une erreur
    raise Exception(f"Aucune commande correspondante trouvée pour l'entrée: '{text}'")

