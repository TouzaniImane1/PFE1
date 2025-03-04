from executors.command_executor import ReadEmailsCommandExecutor

# Créer une instance de la classe
executor = ReadEmailsCommandExecutor()

# Exécuter la commande pour récupérer les e-mails
print("🔍 Test de récupération des e-mails...")
print(executor.execute())
