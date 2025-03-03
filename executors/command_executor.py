import os
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
    def execute(self, command, *args):  # 👈 Accepte plusieurs arguments
        EMAIL = "ton-email@gmail.com"
        PASSWORD = "ton-mot-de-passe"

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
            return "Derniers e-mails :\n" + "\n".join(emails) if emails else "Aucun e-mail trouvé."

        except Exception as e:
            return f"Erreur lors de la récupération des e-mails : {e}"

# ✅ Mapping des commandes vocales
command_map = {
    # 📌 Ouvrir des sites web
    "ouvre google": OpenUrlCommandExecutor("https://www.google.com"),
    "ouvre youtube": OpenUrlCommandExecutor("https://www.youtube.com"),
    "ouvre facebook": OpenUrlCommandExecutor("https://www.facebook.com"),
    "ouvre instagram": OpenUrlCommandExecutor("https://www.instagram.com"),
    "ouvre gmail": OpenUrlCommandExecutor("https://mail.google.com/"),
    "ouvre github": OpenUrlCommandExecutor("https://github.com/"),
    "ouvre whatsapp": OpenUrlCommandExecutor("https://web.whatsapp.com/"),
    "ouvre amazon": OpenUrlCommandExecutor("https://www.amazon.com/"),

    # 📌 Ouvrir des applications locales
    "lance la calculatrice": OpenLocalAppCommandExecutor("calc"),
    "ouvre le bloc-notes": OpenLocalAppCommandExecutor("notepad"),
    "ouvre l'explorateur": OpenLocalAppCommandExecutor("explorer"),
    "capture d'écran": OpenLocalAppCommandExecutor("snippingtool"),

    # 📌 Lire les e-mails
    "lis mes emails": ReadEmailsCommandExecutor(),
}
