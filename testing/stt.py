# stt.py
"""
Handles audio recording from a microphone and runs transcription via Whisper.
"""

import whisper
import pyaudio
import wave
import subprocess
import os
from config import RECORD_SECONDS, SAMPLE_RATE, CHANNELS, WHISPER_MODEL


def record_audio(output_filename="recording.wav"):
    """
    Records audio from the default mic for RECORD_SECONDS and saves to output_filename.
    """
    chunk = 1024
    sample_format = pyaudio.paInt16
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=chunk)

    print(f"Recording for {RECORD_SECONDS} second(s)...")
    frames = []
    # TODO: the record seconds is hard coded here, but it should be a parameter or automatically set
    for _ in range(int(SAMPLE_RATE / chunk * RECORD_SECONDS)):
        data = stream.read(chunk)
        frames.append(data)
    print("Done recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return output_filename


def transcribe_audio_whisper(audio_file):
    """
    Uses the Whisper CLI to transcribe the given audio file.
    """
    # Example: whisper <audio_file> --model base --language en --output_format txt
    # We'll capture the output from whisper's CLI command
    # we could also import whisper as a library, but CLI is working fine.

    print("Transcribing with Whisper...")
    cmd = [
        "whisper",
        audio_file,
        "--model", WHISPER_MODEL,
        "--language", "en",
        "--output_format", "txt"
    ]
    completed_process = subprocess.run(cmd, capture_output=True, text=True)

    if completed_process.returncode != 0:
        print("Whisper CLI error:", completed_process.stderr)
        return None

    # Whisper by default creates a .txt file with the transcript in the same directory
    txt_file = audio_file.replace(".wav", ".txt")
    if os.path.exists(txt_file):
        with open(txt_file, "r", encoding="utf-8") as f:
            transcript = f.read().strip()
        return transcript
    else:
        print("Transcription file not found.")
        return None


# model = whisper.load_model("base")
# result = model.transcribe("recording.wav")
# text = result["text"]
