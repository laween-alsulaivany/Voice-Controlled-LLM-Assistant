# # main.py
# """
# Entry point that ties everything together:
# 1. Record audio
# 2. Transcribe with Whisper
# 3. Route the command (HA or LLM)
# 4. Optionally speak the result using TTS
# """

# from stt import record_audio, transcribe_audio_whisper
# from router import route_command
# from home_assistant import send_to_ha_conversation
# from llm import generate_response
# import pyttsx3


# def text_to_speech(text: str):
#     """
#     Basic text-to-speech using pyttsx3 (offline).
#     """
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()


# def main():
#     # 1. Record audio
#     audio_file = record_audio("command.wav")

#     # 2. Transcribe
#     transcribed_text = transcribe_audio_whisper(audio_file)
#     if not transcribed_text:
#         print("No transcription available.")
#         return

#     print(f"Transcribed Text: {transcribed_text}")

#     # 3. Route the command wether to HA or LLM
#     destination = route_command(transcribed_text)
#     if destination == "HA":
#         response = send_to_ha_conversation(transcribed_text)
#         # The response from HA might not be "human-friendly" text, so we just print it:
#         print("Home Assistant Response:", response)
#         # If we want TTS of a success message:
#         text_to_speech("OK, I've sent your command to Home Assistant.")
#     else:
#         # 4. Fallback to LLM
#         answer = generate_response(transcribed_text)
#         print("LLM Response:", answer)
#         text_to_speech(answer)


# if __name__ == "__main__":
#     main()

from stt import record_audio, transcribe_audio_whisper
from router import route_command
from home_assistant import send_to_ha_conversation
from llm import generate_response
import pyttsx3


def text_to_speech(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def main():
    print("Loading once... Model and other resources are ready!")
    # NOTE: using a while loop to simulate continuous operation and prevent the model from loading each time
    while True:
        user_input = input("\nPress Enter to record or type 'q' to quit: ")
        if user_input.strip().lower() == 'q':
            print("Exiting.")
            break

        # 1. Record audio (or you could do text input for quick tests)
        audio_file = record_audio("command.wav")

        # 2. Transcribe
        transcribed_text = transcribe_audio_whisper(audio_file)
        if not transcribed_text:
            print("No transcription available.")
            continue

        print(f"Transcribed Text: {transcribed_text}")

        # 3. Route
        destination = route_command(transcribed_text)
        if destination == "HA":
            response = send_to_ha_conversation(transcribed_text)
            print("Home Assistant Response:", response)
            text_to_speech("OK, I've sent your command to Home Assistant.")
        else:
            # 4. LLM fallback
            answer = generate_response(transcribed_text)
            print("LLM Response:", answer)
            text_to_speech(answer)


if __name__ == "__main__":
    main()
