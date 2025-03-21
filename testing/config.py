# config.py

import os

# Home Assistant configuration
HOME_ASSISTANT_URL = os.getenv(
    "HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
HOME_ASSISTANT_TOKEN = os.getenv(
    "HOME_ASSISTANT_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZjVkNjhhNDA5ODU0NzlmOWEyMDA5NTJlMzQ4OTlhYiIsImlhdCI6MTc0MjQ0MzE4OCwiZXhwIjoyMDU3ODAzMTg4fQ.vePb9vI5PFB0_yh9NIdBJqVgNyd646d_AF04pOr8DGw")

# Local LLM model config (change this to your actual local path)
MODEL_LOCAL_PATH = os.getenv("MODEL_LOCAL_PATH",
                             "C:/Users/Laween/.cache/huggingface/hub/models--mistralai--Mistral-7B-Instruct-v0.3/snapshots/e0bc86c23ce5aae1db576c8cca6f06f1f73af2db"
                             )

# Whisper parameters (model size, etc.)
# TODO: consider using faster-whisper instead of whisper for faster inference
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

# Audio recording settings
RECORD_SECONDS = int(os.getenv("RECORD_SECONDS", 5))
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))
CHANNELS = int(os.getenv("CHANNELS", 1))
