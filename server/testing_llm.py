# test_llm.py
import logging
import json
from llm import LMStudioFunctionCalling

class DummyDevice:
    def __init__(self):
        self.messages = []
        self.last_response = ""
        self.last_beeper_results = {}
        self.vad = type('obj', (object,), {"visualization": lambda: ""})()
        self.hostname = "test_device"

        # Simple logger that logs to stdout
        self.log = logging.getLogger("DummyDevice")
        self.log.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    def prune_messages(self):
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]

    def stop_listening(self):
        self.log.info("🛑 stop_listening() called")

    def send_audio(self, filename, **kwargs):
        self.log.info(f"🎵 send_audio() called with file: {filename}")

# Basic config for LLM usage without any function calling
config = {
    "llm": {
        "lmstudio_model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "users_name": "TestUser",
        "max_messages": 10,
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "api_key": None,
    },
    "use_notes": False,
    "use_maubot": False,
    "use_home_assistant": False,
    "notes_file": "notes.txt",  # Needed if use_notes is True
}

def main():
    llm = LMStudioFunctionCalling(config)
    device = DummyDevice()

    print("Type your question (Ctrl+C to exit):")
    try:
        while True:
            question = input("🗨️  > ")
            response = llm.askLMStudio(device, question)
            print(f"🤖 Response:\n{response}\n")
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
