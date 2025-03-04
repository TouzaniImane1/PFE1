import os
import pyttsx3
import webbrowser
import imaplib
import email
from email.header import decode_header

class CommandExecutor():
    def execute(self):
        pass

# ✅ Ouvrir des sites web
class OpenUrlCommandExecutor(CommandExecutor):
    def __init__(self, url):
        self.url = url

    def execute(self, command, *args):  # 👈 Accepte plusieurs arguments
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
    def execute(self, command, *args): 
        EMAIL = "imane.tzn392@gmail.com"
        PASSWORD = "lbog ckxy goqj yief"

        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")

            result, data = mail.search(None, "ALL")
            mail_ids = data[0].split()[-3:]

            emails = []
            for mail_id in mail_ids:
                result, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes) and encoding:
                            subject = subject.decode(encoding)
                        emails.append(f"- {subject}")

            mail.logout()
            if emails:
                email_text = "Voici vos derniers e-mails : " + ". ".join(emails)
                print(email_text)
                # LIRE À VOIX HAUTE
                engine = pyttsx3.init()
                engine.say(email_text)
                engine.runAndWait()

                return email_text
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
