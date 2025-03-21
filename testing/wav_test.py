import pyaudio, wave, subprocess

def record_audio(filename, record_secs=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 16000  # sample rate
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format, channels=channels, rate=fs, input=True, frames_per_buffer=chunk)
    frames = []
    print("Recording...")
    for _ in range(int(fs / chunk * record_secs)):
        data = stream.read(chunk)
        frames.append(data)
    print("Done recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

# Record and transcribe
filename = "test.wav"
record_audio(filename, 5)
subprocess.run(["whisper", filename, "--model", "base"])
