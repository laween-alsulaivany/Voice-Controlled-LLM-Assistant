import json
import os
from datetime import datetime
import torch
from pydub import AudioSegment
import soundfile as sf
from rich import print
from kokoro import KPipeline

class KokoroTTS:
    def __init__(self, config):            
        # Load configuration
        self.config = config
        self.jsonfile = config.get('voices_file', 'kokoro_voices.json')
        self.temp_wav_fname = config.get('temp_wav_fname', 'temp.wav')
        self.default_voice = config.get('kokoro_default_voice', 'af_heart')
        self.default_lang = config.get('kokoro_default_lang', 'a')  # 'a' = American English
        
        # Initialize Kokoro pipeline
        self.pipeline = KPipeline(lang_code=self.default_lang)
        
        # Get available voices
        self.voices = self.get_voices()
        for k, v in self.voices.items():
            print(f"{v['name']} \t[dim]({v['voice_id']})[/dim]")
            
    def get_voices(self):
        # For now, we'll create a simple dictionary with default voices
        # In a full implementation, you might want to discover available voices
        voices_dict = {
            "Heart": {
                "voice_id": "af_heart",
                "name": "Heart",
                "lang_code": "a"  # American English
            },
            "Default": {
                "voice_id": "af_heart", 
                "name": "Default",
                "lang_code": "a"
            }
        }
        
        # Save voices to JSON file if it doesn't exist
        if not os.path.exists(self.jsonfile):
            print(f"Creating voice file at [bold]{self.jsonfile}[/]")
            with open(self.jsonfile, 'w') as fp:
                json.dump(voices_dict, fp, indent=4)
        else:
            # Load existing voices file
            with open(self.jsonfile, "r") as f:
                voices_dict = json.load(f)
            print(f"\n🗣️  Loaded {len(voices_dict)} voices from [bold]{self.jsonfile}[/]")
            
        return voices_dict
    
    def get_voice_id(self, device):
        if hasattr(device, 'voice') and device.voice in self.voices:
            return self.voices[device.voice]['voice_id']
        else:
            if hasattr(device, 'log'):
                device.log.warning(f"Voice '{getattr(device, 'voice', None)}' not found, using default {self.default_voice}")
            return self.default_voice
    
    def text_to_speech(self, device, text, path_name="data"):
        # Create directory if it doesn't exist
        os.makedirs(path_name, exist_ok=True)
        
        # Get current timestamp for filename
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Get voice ID
        voice_id = self.get_voice_id(device)
        
        # Get language code - default to American English
        lang_code = self.default_lang
        if hasattr(device, 'voice') and device.voice in self.voices:
            lang_code = self.voices[device.voice].get('lang_code', self.default_lang)
            
        # Log the TTS request
        if hasattr(device, 'log'):
            device.log.debug(f"Generating speech for: '{text[:30]}...' using voice {voice_id}", extra={"highlighter": None})
        
        # Generate speech using Kokoro
        try:
            # Create the generator
            generator = self.pipeline(text, voice=voice_id, speed=1.0)
            
            # We'll only use the first generated segment for simplicity
            # In a more complex implementation, you might want to handle multiple segments
            for _, (_, _, audio) in enumerate(generator):
                # Save to wav file
                output_wav = os.path.join(path_name, f'{voice_id}_{now_str}.wav')
                sf.write(output_wav, audio, 24000)  # Kokoro uses 24kHz sampling rate
                
                # Also save to the temp file location for compatibility
                temp_wav_path = os.path.join(path_name, self.temp_wav_fname)
                sf.write(temp_wav_path, audio, 24000)
                
                if hasattr(device, 'log'):
                    device.log.debug(f"Saved audio to {output_wav}", extra={"highlighter": None})
                
                return self.temp_wav_fname
                
        except Exception as e:
            if hasattr(device, 'log'):
                device.log.error(f"Error generating speech: {str(e)}")
            else:
                print(f"[bold red]Error generating speech: {str(e)}[/]")
            return None