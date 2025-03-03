from executors.command_executor import command_map

def recognize_command(text):
    """
    Associe directement un texte transcrit à une commande définie.
    """
    text = text.lower().strip()

    # Vérifier si le texte correspond exactement à une commande
    if text in command_map:
        return text
    
    # Vérifier si le texte contient une partie clé d'une commande
    for command in command_map.keys():
        if command in text:
            return command

    # Si aucune correspondance n'est trouvée, retourner une erreur
    raise Exception(f"Aucune commande correspondante trouvée pour l'entrée: '{text}'")

