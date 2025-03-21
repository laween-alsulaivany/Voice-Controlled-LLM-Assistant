import pyttsx3

engine = pyttsx3.init()
engine.say("Hello, I am your local voice assistant!")
engine.runAndWait()
engine.stop()
