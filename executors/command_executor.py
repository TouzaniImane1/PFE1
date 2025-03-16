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
import random
import queue
import datetime
import psutil


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

class TakePhotoCommandExecutor:
    def execute(self, command=None, *args):
        """ Ouvre la caméra et capture une photo avec annonces vocales sans bloquer """

        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)  # Sélectionner la première voix disponible
        engine.setProperty("rate", 150)  # Ajuster la vitesse

        def speak_message(message):
            """ Fonction pour parler en arrière-plan avec threading """
            def run():
                print(f"🗣 {message}")
                engine.say(message)
                engine.runAndWait()
            threading.Thread(target=run, daemon=True).start()  # Lancer la voix en parallèle

        # 🔹 Annonce avant d'ouvrir la caméra (en thread pour ne pas bloquer)
        speak_message("Pour prendre une image, appuyez sur espace. Si tu veux fermer la caméra, appuie sur Q.")

        cap = cv2.VideoCapture(0)  # Ouvrir la caméra par défaut

        if not cap.isOpened():
            speak_message("Erreur : Impossible d'ouvrir la caméra.")
            return "Erreur : Impossible d'ouvrir la caméra."

        print("📷 Caméra ouverte. Appuyez sur 'Espace' pour capturer une image ou 'Q' pour quitter.")

        image_captured = False  # Variable pour savoir si une image a été prise

        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Erreur : Impossible de récupérer l'image.")
                break

            cv2.imshow("Caméra - Appuyez sur 'Espace' pour capturer", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(" "):  # Capture d'image avec la barre espace
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)
                print(f"✅ Image capturée et sauvegardée sous {image_path}")
                image_captured = True
                break
            elif key == ord("q"):  # Quitter avec 'q'
                print("❌ Fermeture de la caméra.")
                break

        cap.release()
        cv2.destroyAllWindows()

        # 🔹 Lecture vocale après fermeture ou capture (lancée en thread)
        if image_captured:
            speak_message("Image capturée avec succès.")  # 🔹 Annonce après capture
            return f"Image capturée : {image_path}"
        else:
            speak_message("Fermeture de la caméra.")  # 🔹 Annonce si fermeture sans capture
            return "Caméra fermée sans capture."

class TellJokeCommandExecutor:
    def __init__(self):
        self.jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon ils tombent dans le bateau.",
            "Que dit une noisette quand elle tombe dans l'eau ? Je me noix !",
            "Quel est le comble pour un électricien ? De ne pas être au courant.",
            "Pourquoi les oiseaux ne passent-ils pas leurs diplômes ? Parce qu'ils ont peur de se planter.",
        ]
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

        # Création d'une file d'attente pour les messages à lire
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self.run_speech_loop, daemon=True)
        self.speech_thread.start()

    def run_speech_loop(self):
        """ Boucle qui exécute les messages vocaux sans conflit """
        while True:
            text = self.speech_queue.get()
            if text is None:
                break  # Permet d'arrêter proprement le thread
            self.engine.say(text)
            self.engine.runAndWait()

    def speak(self, text):
        """ Ajoute le texte à la file d'attente pour être lu """
        self.speech_queue.put(text)

    def execute(self, command=None, *args):
        joke = random.choice(self.jokes)
        print(f"🃏 Blague sélectionnée : {joke}")
        self.speak(joke)
        return {"status": "Blague racontée", "joke": joke}

class TellTimeCommandExecutor:
    """ Exécuteur pour annoncer l'heure actuelle """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

    def execute(self, command=None, *args):
        now = datetime.datetime.now()
        time_text = f"Il est {now.hour} heures et {now.minute} minutes."
        print(f"🕰️ {time_text}")
        self.engine.say(time_text)
        self.engine.runAndWait()
        return {"status": "Heure annoncée", "time": time_text}     
    
class TellDateCommandExecutor:
    """ Exécuteur pour annoncer la date actuelle """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

    def execute(self, command=None, *args):
        today = datetime.datetime.now()
        date_text = f"Aujourd'hui, nous sommes le {today.strftime('%A %d %B %Y')}."
        print(f"📅 {date_text}")
        self.engine.say(date_text)
        self.engine.runAndWait()
        return {"status": "Date annoncée", "date": date_text}

class TellBatteryCommandExecutor:
    """ Exécuteur pour annoncer le niveau de batterie """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)

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
        self.engine.say(battery_text)
        self.engine.runAndWait()
        return {"status": "Batterie annoncée", "battery": battery_text}

        # ✅ Ouvrir des sites web
class OpenUrlCommandExecutor(CommandExecutor):
    last_execution_time = 0  # ✅ Stocke le dernier appel

    def __init__(self, url):
        self.url = url

    def execute(self, command=None, *args):
        current_time = time.time()
        if current_time - OpenUrlCommandExecutor.last_execution_time < 1.5:  # ✅ Vérifie le temps écoulé
            print("⏳ Commande ignorée pour éviter une exécution en double.")
            return "Commande ignorée pour éviter une exécution en double."
        
        OpenUrlCommandExecutor.last_execution_time = current_time  # ✅ Mise à jour du temps
        print(f"✅ Exécution unique de la commande pour {self.url}")  
        webbrowser.open(self.url)  # ✅ Maintenant, il ne s'ouvrira qu'une seule fois
        return f"Ouverture de {self.url}"

# ✅ Ouvrir des applications locales
class OpenLocalAppCommandExecutor(CommandExecutor):
    def __init__(self, command):
        self.command = command

    def execute(self, command, *args):
        os.system(self.command)
        return f"Lancement de {self.command}"

# ✅ Lire les e-mails
class ReadEmailsCommandExecutor(CommandExecutor):
   def execute(self, command=None, *args):
        EMAIL = "ton_email@gmail.com"
        PASSWORD = "ton_mot_de_passe_app"

        try:
            # 🔹 Ouvrir Gmail en premier
            webbrowser.open("https://mail.google.com/")
            time.sleep(5)  # Attendre quelques secondes pour laisser le temps d'ouverture

            # Connexion à Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")

            # 🔹 Récupérer les 3 derniers e-mails
            result, data = mail.search(None, "ALL")
            mail_ids = data[0].split()[-3:]  # Prendre les 3 derniers e-mails

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

            mail.logout()  # Fermer la connexion Gmail

            if emails:
                # 🔹 Lire les 3 titres des e-mails
                email_titles = [f"E-mail {i+1} : {email[0]}" for i, email in enumerate(emails)]
                speak_text = "Voici vos trois derniers e-mails. " + " ".join(email_titles)

                print(f"📩 {speak_text}")  # Affichage console
                engine.say(speak_text)
                engine.say("Dites le numéro de l'e-mail que vous voulez écouter.")
                engine.runAndWait()

                # 🔹 Attendre le choix du numéro
                choice = self.recognize_speech()

                # 🔹 Vérifier si c'est un numéro valide
                spoken_numbers = {
                    "un": 1, "premier": 1, "1": 1,
                    "deux": 2, "second": 2, "2": 2,
                    "trois": 3, "troisième": 3, "3": 3
                }

                if choice in spoken_numbers:
                    choice_number = spoken_numbers[choice]
                    choice_index = choice_number - 1  # Convertir en index (0,1,2)

                    if 0 <= choice_index < len(emails):
                        return self.read_email_content(emails[choice_index][1])
                    else:
                        engine.say("Choix invalide. Réessayez en disant un, deux ou trois.")
                        engine.runAndWait()
                        return "Choix invalide."
                else:
                    engine.say("Je n'ai pas compris. Réessayez en disant un, deux ou trois.")
                    engine.runAndWait()
                    return "Commande non reconnue."
            else:
                return "Aucun e-mail trouvé."

        except Exception as e:
            return f"Erreur lors de la récupération des e-mails : {e}"

def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Parlez maintenant...")
            recognizer.adjust_for_ambient_noise(source, duration=1.5)  # Réduction du bruit
            audio = recognizer.listen(source, timeout=7)  # Écoute avec une limite de 7 sec

        try:
            spoken_text = recognizer.recognize_google(audio, language="fr-FR")
            print(f"🎤 Vous avez dit : {spoken_text}")
            return spoken_text.lower()  # Convertir en minuscules pour éviter les erreurs de comparaison
        except sr.UnknownValueError:
            print("⚠️ Je n'ai pas compris.")
            return None
        except sr.RequestError:
            print("⚠️ Erreur de connexion à l'API de reconnaissance vocale.")
            return None

def read_email_content(self, msg):
        # Extraction du contenu
        email_content = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    email_content = part.get_payload(decode=True).decode()
                    break
        else:
            email_content = msg.get_payload(decode=True).decode()

        # Lire le contenu de l’e-mail à voix haute
        engine.say(f"Voici le contenu de l’e-mail sélectionné : {email_content}")
        engine.runAndWait()
        print(f"📩 Contenu de l’e-mail : {email_content}")
        return email_content

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
        # 📌 Raconter des blagues
    "raconte une blague": TellJokeCommandExecutor(),
    "dis-moi une blague": TellJokeCommandExecutor(),
    "j'ai envie de rire": TellJokeCommandExecutor(),
    "raconte-moi quelque chose de drôle": TellJokeCommandExecutor(),
    "je suis ennuier": TellJokeCommandExecutor(),
    "je m'ennuie": TellJokeCommandExecutor(),
    "une blague": TellJokeCommandExecutor(),
    "moi une blague": TellJokeCommandExecutor(),
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





}
