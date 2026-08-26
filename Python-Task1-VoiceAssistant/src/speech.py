import os

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv

load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init()
MIC_DEVICE_INDEX = 0
LANG = os.getenv("ASSISTANT_LANG", "en-US")


def listen_microphone():
    try:
        with sr.Microphone(device_index=MIC_DEVICE_INDEX) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    except (OSError, ValueError):
        return ""

    try:
        return recognizer.recognize_google(audio, language=LANG)
    except (sr.UnknownValueError, sr.RequestError):
        return ""


def speak(text: str):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


if __name__ == "__main__":
    phrase = listen_microphone()
    print("You said:", phrase)
    speak("Hello! How can I help you?")
