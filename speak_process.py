import pyttsx3
import sys

def speak(message):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(message)
    engine.runAndWait()
    engine.stop()

if __name__ == "__main__":
    msg = sys.argv[1]
    speak(msg)
