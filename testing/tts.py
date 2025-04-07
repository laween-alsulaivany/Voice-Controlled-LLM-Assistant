import time
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
# engine.say("Hello, I am your local voice assistant!")
engine.save_to_file("Hello, I am your local voice assistant!", "output.wav")
engine.runAndWait()
time.sleep(5)
engine.stop()
#
