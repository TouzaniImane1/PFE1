import os
import pyttsx3
import webbrowser
import imaplib
import email
from email.header import decode_header
import speech_recognition as sr
import time
import cv2
import threading
import datetime
import psutil
import subprocess
import re
import locale
import pyautogui

# Initialiser le moteur de synthèse vocale
engine = pyttsx3.init()

def set_first_voice():
    """
    Sélectionne et applique uniquement la première voix disponible.
    """
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)  # Utiliser la première voix détectée
    engine.setProperty('rate', 130)  # Réduction de la vitesse pour une lecture plus naturelle

set_first_voice()

def speak_text(text):
     """ Fonction pour exécuter la synthèse vocale sans bloquer. """
     def run():
        try:
            engine = pyttsx3.init()
            engine.stop()  # ✅ Arrête toute exécution en cours
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Erreur de synthèse vocale : {e}")

     threading.Thread(target=run, daemon=True).start()  # ✅ Exécuter en thread pour ne pas bloquer



class CommandExecutor():
    def execute(self, command=None, *args):
        pass

class BaseCommandExecutor:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)  

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()
        self.engine.stop()  # Ajouté pour éviter le "run loop already started"
        
class TakePhotoCommandExecutor:
    def speak_async(self, message):
        """ Faire parler l'assistant en parallèle """
        def speak():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.say(message)
            engine.runAndWait()
        threading.Thread(target=speak, daemon=True).start()

    def execute(self, command=None, *args):
        """ Ouvre la caméra et capture une photo avec annonces vocales non-bloquantes """

        # 🔹 Ouvrir la caméra D'ABORD
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.speak_async("Erreur : Impossible d'ouvrir la caméra.")
            return "Erreur : Impossible d'ouvrir la caméra."

        print("📷 Caméra ouverte.")

        # 🔹 Pendant que la caméra tourne → annonce vocale
        self.speak_async("Pour prendre une image, appuyez sur espace. Si tu veux fermer la caméra, appuie sur Q.")

        image_captured = False

        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Erreur : Impossible de récupérer l'image.")
                break

            cv2.imshow("Caméra - Appuyez sur 'Espace' pour capturer", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):  # Capture image
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)
                print(f"✅ Image capturée et sauvegardée sous {image_path}")
                image_captured = True
                break
            elif key == ord("q"):  # Quitter
                print("❌ Fermeture de la caméra.")
                break

        cap.release()
        cv2.destroyAllWindows()

        # 🔹 Parler après capture/fermeture
        if image_captured:
            self.speak_async("Image capturée avec succès.")
            return f"Image capturée : {image_path}"
        else:
            self.speak_async("Caméra fermée sans capture.")
            return "Caméra fermée sans capture."
        
class TakeScreenshotCommandExecutor:
    def execute(self, command=None, *args):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            save_path = f"C:/Users/ADS/Pictures/{filename}"  # change si nécessaire

            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)

            print(f"📸 Capture enregistrée sous {save_path}")
            subprocess.Popen(["python", "speak_process.py", "Capture d’écran enregistrée."])
            return f"Capture d’écran enregistrée dans {save_path}."
        except Exception as e:
            print(f"❌ Erreur de capture : {str(e)}")
            return f"Erreur lors de la capture : {str(e)}"

class TellTimeCommandExecutor:
    """ Exécuteur pour annoncer l'heure actuelle """


    def execute(self, command=None, *args):
        now = datetime.datetime.now()
        time_text = f"Il est {now.hour} heures et {now.minute} minutes."
        print(f"🕰️ {time_text}")
        subprocess.Popen(["python", "speak_process.py", time_text])
        return time_text
    
class TellDateCommandExecutor:
    """ Exécuteur pour annoncer la date actuelle """

    def execute(self, command=None, *args):
        try:
            # 🟢 Définir la locale en français
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR')  # Windows fallback
            except locale.Error:
                print("⚠️ Locale fr_FR non disponible sur ce système.")
                # Pas d'arrêt du script, il lira en anglais dans ce cas

        today = datetime.datetime.now()
        date_text = f"Aujourd'hui, nous sommes le {today.strftime('%A %d %B %Y')}."
        print(f"📅 {date_text}")

        # 🔊 Lancer le processus de lecture
        subprocess.Popen(["python", "speak_process.py", date_text])
        return date_text


class TellBatteryCommandExecutor:
    """ Exécuteur pour annoncer le niveau de batterie """


    def execute(self, command=None, *args):
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = battery.power_plugged
            charge_status = "branché" if plugged else "non branché"
            battery_text = f"Le niveau de batterie est de {percent} pour cent et votre PC est {charge_status}."
        else:
            battery_text = "Je ne peux pas détecter la batterie de votre PC."

        print(f"🔋 {battery_text}")
        subprocess.Popen(["python", "speak_process.py", battery_text])
        return battery_text

        # ✅ Ouvrir des sites web
class OpenDynamicUrlCommandExecutor:
    def execute(self, command, *args):
        if "ouvre " in command or "ouvrir " in command or "lance " in command:
            mots = command.split()
            for mot in mots:
                if "." not in mot and mot not in ["ouvre", "ouvrir", "lance"]:
                    site = mot.replace(" ", "").lower()
                    url = f"https://www.{site}.com/"
                    try:
                        print(f"🌐 Ouverture de : {url}")
                        webbrowser.open(url)
                        return f"Ouverture de {site}"
                    except Exception as e:
                        return f"Erreur : impossible d’ouvrir {site}. {str(e)}"
        return "Commande non reconnue pour l'ouverture d'un site."

        # ✅ Ouvrir des sites web
class OpenUrlCommandExecutor(CommandExecutor):
    last_execution_time = 0  # ✅ Stocke le dernier appel

    def __init__(self, url):
        self.url = url
        self.message = f"J'ai ouvert le site {url}"

    def execute(self, command=None, *args):
        current_time = time.time()
        if current_time - OpenUrlCommandExecutor.last_execution_time < 1.5:  # ✅ Vérifie le temps écoulé
            print("⏳ Commande ignorée pour éviter une exécution en double.")
            return "Commande ignorée pour éviter une exécution en double."
        
        OpenUrlCommandExecutor.last_execution_time = current_time  # ✅ Mise à jour du temps
        print(f"✅ Exécution unique de la commande pour {self.url}")  
        webbrowser.open(self.url)  # ✅il ne s'ouvrira qu'une seule fois
        return f"Ouverture de {self.url}"

# ✅ Ouvrir des applications locales
class OpenLocalAppCommandExecutor(CommandExecutor):
    def __init__(self, command):
        self.command = command
        self.message = f"J'ai ouvert l'application {command}"

    def execute(self, command, *args):
        os.system(self.command)
        return f"Lancement de {self.command}"
    
# ✅ Lire les e-mails
class ReadEmailsCommandExecutor:
    def __init__(self):
        self.last_emails = []

    def speak_sync(self, message):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.say(message)
        engine.runAndWait()

    def fetch_emails(self):
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            imap.login("imane.tzn392@gmail.com", "lbog ckxy goqj yief")
            imap.select("inbox")
            status, messages = imap.search(None, "ALL")
            messages = messages[0].split()
            latest = messages[-3:] if len(messages) >= 3 else messages

            infos = []
            for num in reversed(latest):
                res, msg_data = imap.fetch(num, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                sender = msg.get("From").split("<")[0].strip()
                content = self.extract_short_content(msg)
                infos.append((sender, subject, content))
            imap.logout()
            return infos

        except Exception as e:
            print(f"❌ Erreur : {e}")
            return []

    def extract_short_content(self, msg):
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        text = part.get_payload(decode=True).decode(errors="ignore")
                        return self.clean_text(text)
            else:
                text = msg.get_payload(decode=True).decode(errors="ignore")
                return self.clean_text(text)
        except:
            return "Contenu illisible."
        return "Contenu vide."
    def extract_content(self, msg):
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode(errors="ignore")
            else:
                return msg.get_payload(decode=True).decode(errors="ignore")
        except Exception as e:
            print(f"⚠️ Erreur de décodage du contenu : {e}")
        return "Contenu illisible."


    def clean_text(self, text):
        text = text.replace("\r", " ").replace("\n", " ").strip()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"www\.\S+", "", text)
        keywords = ["En savoir plus", "Se désabonner", "Cliquez ici", "Privacy", "Unsubscribe", "Aide", "Voir plus"]
        for keyword in keywords:
            text = text.split(keyword)[0]
        phrases = text.split(".")
        cleaned = ". ".join(phrases[:2]).strip()
        return cleaned + "."
    def execute(self, *args):
        try:
            self.last_emails = self.fetch_emails()
            if not self.last_emails:
                return {"status": "Aucun e-mail trouvé."}

            full_message = ""
            for idx, (sender, subject, msg) in enumerate(self.last_emails, 1):
                content = self.extract_content(msg)
                content = self.clean_text(content)
                full_message += f"E-mail {idx} de {sender}, sujet : {subject}. "

            print("🔊", full_message)
            self.speak_sync(full_message)

            return {"status": "Lecture des e-mails terminée."}

        except Exception as e:
            print(f"❌ Erreur générale : {e}")
            return {"status": f"Erreur pendant la lecture des e-mails : {str(e)}"}


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
    "ouvre w3schools": OpenUrlCommandExecutor("https://www.w3schools.com/"),
    "w3schools": OpenUrlCommandExecutor("https://www.w3schools.com/"),
    "lance w3schools": OpenUrlCommandExecutor("https://www.w3schools.com/"),


    # 📌 Lire les e-mails
    "lire les emails": ReadEmailsCommandExecutor(),
    "lis les emails": ReadEmailsCommandExecutor(),
    "lire des emails": ReadEmailsCommandExecutor(),
    "lis mes e-mails": ReadEmailsCommandExecutor(),
    "lire les e-mails": ReadEmailsCommandExecutor(),
    "lire mes e-mails": ReadEmailsCommandExecutor(),
    "lis les e-mails": ReadEmailsCommandExecutor(),
    "lis des e-mails": ReadEmailsCommandExecutor(),
    "lire des e-mails": ReadEmailsCommandExecutor(),
    "Mes e-mails": ReadEmailsCommandExecutor(),
    "Des e-mails": ReadEmailsCommandExecutor(),
    "les e-mails": ReadEmailsCommandExecutor(),

    "ouvre la caméra": TakePhotoCommandExecutor(),
    "lance la caméra": TakePhotoCommandExecutor(),
    "ouvrir la caméra": TakePhotoCommandExecutor(),
    "démarre la caméra": TakePhotoCommandExecutor(),    
    "la caméra": TakePhotoCommandExecutor(),
    "caméra": TakePhotoCommandExecutor(),
    "prends une photo": TakePhotoCommandExecutor(),
    "capture une photo": TakePhotoCommandExecutor(),
    "prends un selfie": TakePhotoCommandExecutor(),
    "capture un selfie": TakePhotoCommandExecutor(),
    "photo": TakePhotoCommandExecutor(),
    "une photo": TakePhotoCommandExecutor(),
    "selfie": TakePhotoCommandExecutor(),
    "un selfie": TakePhotoCommandExecutor(),
     
 # 📌 Heure actuelle
    "quelle heure est-il": TellTimeCommandExecutor(),
    "donne-moi l'heure": TellTimeCommandExecutor(),
    "il est quelle heure": TellTimeCommandExecutor(),
    "l'heure": TellTimeCommandExecutor(),

    # 📌 Date actuelle
    "quelle est la date d'aujourd'hui": TellDateCommandExecutor(),
    "donne-moi la date": TellDateCommandExecutor(),
    "quelle est la date": TellDateCommandExecutor(),
    "la date": TellDateCommandExecutor(),

    # 📌 Batterie du PC
    "quel est le niveau de batterie": TellBatteryCommandExecutor(),
    "donne-moi le pourcentage de batterie": TellBatteryCommandExecutor(),
    "quelle est l'autonomie restante": TellBatteryCommandExecutor(),
    "donne-moi la batterie": TellBatteryCommandExecutor(),
    "la batterie": TellBatteryCommandExecutor(),

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
    "word": OpenLocalAppCommandExecutor("winword"),
    "ouvre word": OpenLocalAppCommandExecutor("winword"),
    "lance word": OpenLocalAppCommandExecutor("winword"),
    "excel": OpenLocalAppCommandExecutor("excel"),
    "ouvre excel": OpenLocalAppCommandExecutor("excel"),
    "lance excel": OpenLocalAppCommandExecutor("excel"),
    "powerpoint": OpenLocalAppCommandExecutor("powerpnt"),
    "ouvre powerpoint": OpenLocalAppCommandExecutor("powerpnt"),
    "lance powerpoint": OpenLocalAppCommandExecutor("powerpnt"),
    "chrome": OpenLocalAppCommandExecutor("chrome"),
    "ouvre chrome": OpenLocalAppCommandExecutor("chrome"),
    "lance chrome": OpenLocalAppCommandExecutor("chrome"),
    "edge": OpenLocalAppCommandExecutor("msedge"),
    "ouvre edge": OpenLocalAppCommandExecutor("msedge"),
    "lance edge": OpenLocalAppCommandExecutor("msedge"),
    "paint": OpenLocalAppCommandExecutor("mspaint"),
    "ouvre paint": OpenLocalAppCommandExecutor("mspaint"),
    "lance paint": OpenLocalAppCommandExecutor("mspaint"),
    "invite de commandes": OpenLocalAppCommandExecutor("cmd"),
    "terminal": OpenLocalAppCommandExecutor("cmd"),
    "paramètres": OpenLocalAppCommandExecutor("ms-settings:"),
    "ouvre les paramètres": OpenLocalAppCommandExecutor("ms-settings:"),

    # 📌 Caprure d'écran
    "ouvre la capture d'écran": TakeScreenshotCommandExecutor(),
    "lance la capture d'écran": TakeScreenshotCommandExecutor(),
    "la capture d'écran": TakeScreenshotCommandExecutor(),
    "capture d'écran": TakeScreenshotCommandExecutor(),
    "capture": TakeScreenshotCommandExecutor(),
    "prends une capture": TakeScreenshotCommandExecutor(),
    "capture écran": TakeScreenshotCommandExecutor(),
    "prends une capture d'écran": TakeScreenshotCommandExecutor(),
    "fait une capture": TakeScreenshotCommandExecutor(),
    "screen": TakeScreenshotCommandExecutor(),

 # Microsoft Word
    




}
