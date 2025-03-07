import os
import pyttsx3
import webbrowser
import imaplib
import email
from email.header import decode_header
import speech_recognition as sr
import time


class CommandExecutor():
    def execute(self):
        pass

# ✅ Ouvrir des sites web
class OpenUrlCommandExecutor(CommandExecutor):
    def __init__(self, url):
        self.url = url

    def execute(self, command=None, *args):  # 👈 Accepte plusieurs arguments
        webbrowser.open(self.url)
        return f"Ouverture de {self.url}"

# ✅ Ouvrir des applications locales
class OpenLocalAppCommandExecutor(CommandExecutor):
    def __init__(self, command):
        self.command = command

    def execute(self, command, *args):  # 👈 Accepte plusieurs arguments
        os.system(self.command)
        return f"Lancement de {self.command}"

# ✅ Lire les e-mails
class ReadEmailsCommandExecutor(CommandExecutor):
   def execute(self, command=None, *args): 
        EMAIL = "imane.tzn392@gmail.com"
        PASSWORD = "lbog ckxy goqj yief"

        try:
            # 🔹 Connexion à la boîte e-mail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")

            # 🔹 Récupérer les 3 derniers e-mails
            result, data = mail.search(None, "ALL")
            mail_ids = data[0].split()[-3:]  # Prendre les 3 derniers

            emails = []
            for mail_id in mail_ids:
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes) and encoding:
                            subject = subject.decode(encoding)
                        emails.append((subject, msg))

            mail.logout()  # Fermer la connexion

            if emails:
                # 🔹 Annoncer les e-mails à voix haute
                email_titles = "\n".join([f"{i+1}. {email[0]}" for i, email in enumerate(emails)])
                engine = pyttsx3.init()
                engine.say("Voici vos trois derniers e-mails. Dis le numéro de celui que tu veux écouter : un, deux ou trois.")
                engine.runAndWait()
                
                for i, email_data in enumerate(emails):
                    engine.say(f"E-mail {i+1} : {email_data[0]}")
                    engine.runAndWait()
                    time.sleep(2)  # Pause pour éviter une lecture trop rapide

                # 🔹 Attendre la réponse de l'utilisateur
                def recognize_speech():
                    recognizer = sr.Recognizer()
                    with sr.Microphone() as source:
                        print("🔊 Dis le numéro de l'e-mail (1, 2 ou 3)...")
                        engine.say("Dis maintenant le numéro de l’e-mail.")
                        engine.runAndWait()
                        recognizer.adjust_for_ambient_noise(source, duration=1.5)
                        audio = recognizer.listen(source, timeout=7)

                    try:
                        spoken_text = recognizer.recognize_google(audio, language="fr-FR")
                        print(f"🎤 Tu as dit : {spoken_text}")
                        return spoken_text
                    except sr.UnknownValueError:
                        return None
                    except sr.RequestError:
                        return None

                # 🔹 Mappage des nombres parlés
                spoken_numbers = {
                    "un": 1, "premier": 1, "1": 1,
                    "deux": 2, "second": 2, "2": 2,
                    "trois": 3, "troisième": 3, "3": 3
                }
                choice = recognize_speech()
                choice_number = spoken_numbers.get(choice.lower()) if choice else None

                if choice_number is None:
                    engine.say("Je n'ai pas compris. Réessaie en disant un, deux ou trois.")
                    engine.runAndWait()
                    print("Commande non reconnue.")
                    return "Commande non reconnue."
                
                choice_index = choice_number - 1  # Convertir en index (0,1,2)
                if 0 <= choice_index < len(emails):
                    msg = emails[choice_index][1]  # Récupérer le message e-mail

                    # 🔹 Extraction du contenu de l’e-mail
                    email_content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                email_content = part.get_payload(decode=True).decode()
                                break
                    else:
                        email_content = msg.get_payload(decode=True).decode()

                    # 🔹 Lecture du contenu de l’e-mail
                    engine.say(f"Voici le contenu de l’e-mail : {email_content}")
                    engine.runAndWait()
                    print(f"📩 Contenu de l’e-mail : {email_content}")
                    return email_content
                else:
                    engine.say("Choix invalide. Réessaie en disant un, deux ou trois.")
                    engine.runAndWait()
                    print("Choix invalide.")
                    return "Choix invalide."
            else:
                return "Aucun e-mail trouvé."

        except Exception as e:
            return f"Erreur lors de la récupération des e-mails : {e}"

# ✅ Mapping des commandes vocales
command_map = {
    # 📌 Ouvrir des sites web
    "ouvre google": OpenUrlCommandExecutor("https://www.google.com"),
    "google": OpenUrlCommandExecutor("https://www.google.com"),
    "lance google": OpenUrlCommandExecutor("https://www.google.com"),
    "ouvrir google": OpenUrlCommandExecutor("https://www.google.com"),
    "youtube": OpenUrlCommandExecutor("https://www.youtube.com"),
    "ouvrir youtube": OpenUrlCommandExecutor("https://www.youtube.com"),
    "lance youtube": OpenUrlCommandExecutor("https://www.youtube.com"),
    "ouvre youtube": OpenUrlCommandExecutor("https://www.youtube.com"),
    "ouvrir facebook": OpenUrlCommandExecutor("https://www.facebook.com"),
    "lance facebook": OpenUrlCommandExecutor("https://www.facebook.com"),
    "facebook": OpenUrlCommandExecutor("https://www.facebook.com"),
    "ouvre facebook": OpenUrlCommandExecutor("https://www.facebook.com"),
    "ouvre instagram": OpenUrlCommandExecutor("https://www.instagram.com"),
    "ouvrir instagram": OpenUrlCommandExecutor("https://www.instagram.com"),
    "lance instagram": OpenUrlCommandExecutor("https://www.instagram.com"),
    "instagram": OpenUrlCommandExecutor("https://www.instagram.com"),
    "ouvre gmail": OpenUrlCommandExecutor("https://mail.google.com/"),
    "gmail": OpenUrlCommandExecutor("https://mail.google.com/"),
    "lance gmail": OpenUrlCommandExecutor("https://mail.google.com/"),
    "ouvrir gmail": OpenUrlCommandExecutor("https://mail.google.com/"),
    "ouvre github": OpenUrlCommandExecutor("https://github.com/"),
    "github": OpenUrlCommandExecutor("https://github.com/"),
    "ouvrir github": OpenUrlCommandExecutor("https://github.com/"),
    "lance github": OpenUrlCommandExecutor("https://github.com/"),
    "ouvre whatsapp": OpenUrlCommandExecutor("https://web.whatsapp.com/"),
    "whatsapp": OpenUrlCommandExecutor("https://web.whatsapp.com/"),
    "ouvrir whatsapp": OpenUrlCommandExecutor("https://web.whatsapp.com/"),
    "lance whatsapp": OpenUrlCommandExecutor("https://web.whatsapp.com/"),
    "ouvre amazon": OpenUrlCommandExecutor("https://www.amazon.com/"),
    "amazon": OpenUrlCommandExecutor("https://www.amazon.com/"),
    "ouvrir amazon": OpenUrlCommandExecutor("https://www.amazon.com/"),
    "lance amazon": OpenUrlCommandExecutor("https://www.amazon.com/"),


    # 📌 Ouvrir des applications locales
    "lance la calculatrice": OpenLocalAppCommandExecutor("calc"),
    "ouvre la calculatrice": OpenLocalAppCommandExecutor("calc"),
    "lance ma calculatrice": OpenLocalAppCommandExecutor("calc"),
    "ouvre ma calculatrice": OpenLocalAppCommandExecutor("calc"),
    "la calculatrice": OpenLocalAppCommandExecutor("calc"),
    "ma calculatrice": OpenLocalAppCommandExecutor("calc"),
    "calculatrice": OpenLocalAppCommandExecutor("calc"),
    "le bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    "bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    "ouvre le bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    "lance le bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    "lance bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    " l'explorateur": OpenLocalAppCommandExecutor("explorer"),
    "l'explorateur de fichiers": OpenLocalAppCommandExecutor("explorer"),
    "ouvre l'explorateur": OpenLocalAppCommandExecutor("explorer"),
    "ouvre l'explorateur de fichiers": OpenLocalAppCommandExecutor("explorer"),
    "lance l'explorateur": OpenLocalAppCommandExecutor("explorer"),
    "lance l'explorateur de fichiers": OpenLocalAppCommandExecutor("explorer"),
    "ouvre l'explorateur": OpenLocalAppCommandExecutor("explorer"),
    "capture d'écran": OpenLocalAppCommandExecutor("snippingtool"),
    "ouvre la capture d'écran": OpenLocalAppCommandExecutor("snippingtool"),
    "lance la capture d'écran": OpenLocalAppCommandExecutor("snippingtool"),
    "la capture d'écran": OpenLocalAppCommandExecutor("snippingtool"),


    # 📌 Lire les e-mails
    "lis mes e-mails": ReadEmailsCommandExecutor(),
    "lire mes e-mails": ReadEmailsCommandExecutor(),
    "lis les e-mails": ReadEmailsCommandExecutor(),
    "lis des e-mails": ReadEmailsCommandExecutor(),
    "lire des e-mails": ReadEmailsCommandExecutor(),
    "Mes e-mails": ReadEmailsCommandExecutor(),
    "Des e-mails": ReadEmailsCommandExecutor(),
    "les e-mails": ReadEmailsCommandExecutor(),




}
