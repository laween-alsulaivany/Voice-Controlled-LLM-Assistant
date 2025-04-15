import dateparser
import json
import os
import requests
import time
from datetime import datetime, timedelta
from dateutil import tz
from rich import print

class KoboldCPPConnector:
    def __init__(self, config):
        self.config = config
        self.kobold_url = config.get('kobold', {}).get('url', 'http://localhost:5001/api')
        self.functions = self.setup_functions()
        self.debug = config.get('kobold', {}).get('debug', False)
        
    def setup_functions(self):
        """Set up available functions based on configuration."""
        functions = []
        USERS_NAME = self.config['llm']['users_name']

        # Add notes functions if enabled
        if(self.config['use_notes']):
            functions += [
                # Notes functions as before...
            ]

        # Add Home Assistant functions if enabled, with better error handling
        if(self.config['use_home_assistant']):
            try:
                with open('credentials.json') as json_file:
                    cred = json.load(json_file)
                
                HA_URL = cred['home_assistant_url']
                HA_TOKEN = cred['home_assistant_token']

                print(f"\n🏡 Attempting to connect to Home Assistant at {HA_URL}")
                
                ha_headers = {
                    "Authorization": f"Bearer {HA_TOKEN}",
                }
                device_entity_ids = []
                url = f"{HA_URL}api/states"
                
                # Add timeout and better error handling
                try:
                    response = requests.get(url, headers=ha_headers, timeout=5)
                    states = response.json()

                    light_states = [state for state in states if state['entity_id'].startswith('light.')]

                    if(len(light_states)==0):
                        print("[orange] No lights found in Home Assistant, skipping light control function [/]")
                    else:
                        for light_state in light_states:
                            device_entity_ids.append(light_state['entity_id'])
                            print(f"{'💡' if light_state['state']=='on' else '🌑'}  {light_state['entity_id']}")

                        functions.append({
                            "name": "control_light",
                            "description": "Control a light or multiple lights in the smart home system",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "entity_id": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": device_entity_ids
                                        },
                                        "description": "The entity IDs of the lights to control",
                                    },
                                    "brightness": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 255,
                                        "description": "The brightness level to set the light(s) to, ranging from 0 (off) to 255 (max brightness)",
                                    },
                                    "rgb_color": {
                                        "type": "array",
                                        "items": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 255
                                        },
                                        "maxItems": 3,
                                        "description": "The RGB color to set the light(s) to, represented as an array with three integers ranging from 0 to 255.",
                                    }
                                },
                                "required": ["entity_id"],
                            },
                        })
                    switch_states = [state for state in states if state['entity_id'].startswith('switch.') and 'fan' in state['entity_id']]
    
                    if(len(switch_states) > 0):
                        fan_entity_ids = []
                        for switch_state in switch_states:
                            fan_entity_ids.append(switch_state['entity_id'])
                            print(f"{'🔌 ON' if switch_state['state']=='on' else '🔌 OFF'}  {switch_state['entity_id']}")
                        
                        functions.append({
                            "name": "control_fan",
                            "description": "Turn a fan on or off using a switch",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "entity_id": {
                                        "type": "string",
                                        "enum": fan_entity_ids,
                                        "description": "The entity ID of the fan switch to control",
                                    },
                                    "state": {
                                        "type": "string",
                                        "enum": ["on", "off"],
                                        "description": "The state to set the fan to (on or off)",
                                    }
                                },
                                "required": ["entity_id", "state"],
                            },
                        })
                except requests.exceptions.Timeout:
                    print("[red]Connection to Home Assistant timed out. Light control function will not be available.[/]")
                except requests.exceptions.ConnectionError as e:
                    print(f"[red]Connection error to Home Assistant: {e}[/]")
                    print("[red]Home Assistant functions will not be available.[/]")
                except Exception as e:
                    print(f"[red]Error setting up Home Assistant functions: {e}[/]")
            except Exception as e:
                print(f"[red]Error loading credentials for Home Assistant: {e}[/]")
                print("[red]Home Assistant functions will not be available.[/]")

        # Additional functions can be added here
        
        return functions
    
    def build_prompt(self, device, user_input):
        """Build the prompt for KoboldCPP with context shifting in mind."""
        # Check if this is the first interaction or if we need to rebuild the prompt
        if not hasattr(device, 'cached_prompt') or device.cached_prompt is None:
            # Build the initial system prompt
            current_time = datetime.now().strftime("%I:%M %p on %A %B %d, %Y")
            
            # Format available functions for the prompt
            functions_str = ""
            for func in self.functions:
                functions_str += f"Function: {func['name']}\n"
                functions_str += f"Description: {func['description']}\n"
                functions_str += f"Parameters: {json.dumps(func['parameters'], indent=2)}\n\n"
            
            # Build the system prompt with instructions
            system_prompt = f"""You are a friendly assistant to the user, {self.config['llm']['users_name']}, and you ALWAYS respond in less than 20 words. You are observant of all the details in the data you have in order to come across as highly observant, emotionally intelligent and humanlike in your responses.

The current time and date is {current_time}

# IMPORTANT INSTRUCTIONS:
Your responses MUST follow this exact structure:
1. FIRST LINE: A short spoken response (under 20 words) that will be read aloud
2. THEN: Any function calls using <functioncall> JSON syntax if needed

# AVAILABLE FUNCTIONS:
{functions_str}

# EXAMPLES:
User: Turn off the light
AI: Light turned off.
<functioncall> {{"name":"control_light","arguments":{{"entity_id":["light.light"],"brightness":0}}}}

User: What time is it?
AI: It's currently {current_time}.

User: Remember that I need to buy milk tomorrow
AI: I'll remember you need to buy milk tomorrow.
<functioncall> {{"name":"add_note","arguments":{{"note":"Buy milk tomorrow"}}}}

User: Turn the living room lights blue
AI: Setting living room lights to blue for you.
<functioncall> {{"name":"control_light","arguments":{{"entity_id":["light.living_room_rgbww_lights"],"rgb_color":[0,0,255]}}}}

User: Turn on the fan
AI: Turning on the fan.
<functioncall> {{"name":"control_fan","arguments":{{"entity_id":"switch.fan","state":"on"}}}}

User: Turn off the fan
AI: Fan turned off.
<functioncall> {{"name":"control_fan","arguments":{{"entity_id":"switch.fan","state":"off"}}}}

# Conversation starts now:
"""
            device.cached_prompt = system_prompt
            device.context_history = ""
            
        # Add the new user input to the conversation history
        conversation = f"{device.context_history}User: {user_input}\nAI: "
        
        # Construct the full prompt for KoboldCPP
        full_prompt = device.cached_prompt + conversation
        
        return full_prompt, conversation
    
    def generate_response(self, device, prompt):
        """Generate a response from KoboldCPP."""
        # KoboldCPP API parameters
        params = {
            "prompt": prompt,
            "max_context_length": self.config.get('kobold', {}).get('max_context_length', 2048),
            "max_length": self.config.get('kobold', {}).get('max_length', 200),
            "temperature": self.config.get('kobold', {}).get('temperature', 0.7),
            "top_p": self.config.get('kobold', {}).get('top_p', 0.9),
            "top_k": self.config.get('kobold', {}).get('top_k', 40),
            "rep_pen": self.config.get('kobold', {}).get('rep_pen', 1.1),
            "stop_sequence": ["User:", "\nUser:"],
            "stream": True  #TODO: Make this a config option
        }
        
        try:
            if self.debug:
                print(f"\n🔍 DEBUG: Sending prompt to KoboldCPP:\n{prompt}")
            
            # Make the API request to KoboldCPP
            response = requests.post(f"{self.kobold_url}/v1/generate", json=params)
            
            if response.status_code != 200:
                return f"Error: KoboldCPP returned status code {response.status_code}"
            
            # Parse the response
            result = response.json()
            if self.debug:
                print(f"\n🔍 DEBUG: KoboldCPP response:\n{result}")
            
            generated_text = result.get('results', [{}])[0].get('text', '')
            
            # Clean up the response
            if 'User:' in generated_text:
                generated_text = generated_text.split('User:')[0].strip()
                
            return generated_text
            
        except Exception as e:
            return f"Error: Failed to generate response from KoboldCPP: {str(e)}"
    
    def parse_response(self, text):
        """Parse the generated text into spoken response and function calls."""
        lines = text.strip().split('\n')
        
        # First line is the spoken response
        spoken_response = lines[0] if lines else ""
        
        # Look for function calls
        function_calls = []
        for line in lines[1:]:
            if '<functioncall>' in line:
                # Extract JSON from the functioncall tag
                try:
                    function_str = line.replace('<functioncall>', '').replace('</functioncall>', '').strip()
                    # Add debug print
                    print(f"🔍 Found function call: {function_str}")
                    function_data = json.loads(function_str)
                    function_calls.append(function_data)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Warning: Failed to parse function call: {line}")
                    print(f"⚠️ Error details: {e}")
        
        # Add debug print for results
        print(f"🔍 Parsed response: spoken={spoken_response}, functions={function_calls}")
        
        return spoken_response, function_calls
    
    def execute_functions(self, device, function_calls):
        """Execute the identified function calls."""
        results = []
        
        for function_call in function_calls:
            function_name = function_call.get('name')
            function_args = function_call.get('arguments', {})
            
            result = None
            
            # Notes functions
            if function_name == 'add_note':
                result = self.add_note(device, **function_args)
            elif function_name == 'get_notes':
                result = self.get_notes(device, **function_args)
            
            # Home Assistant functions
            elif function_name == 'control_light':
                result = self.control_light(device, **function_args)
            elif function_name == 'control_fan':
                result = self.control_fan(device, **function_args)
            
            results.append({
                'function': function_name,
                'result': result
            })
        
        return results
            
    def add_note(self, device, note):
        """Add a note to the notes file."""
        timestamp = datetime.now().isoformat()
        note_obj = {
            'timestamp': timestamp,
            'note': note
        }
        try:
            with open(self.config['notes_file'], 'a') as file:
                file.write(json.dumps(note_obj))
                file.write('\n')
            return "Added note successfully"
        except Exception as e:
            device.log.error(f"Error adding note: {e}")
            return f"Error adding note: {str(e)}"

    def get_notes(self, device, day):
        """Get notes from a specific day."""
        query_date = dateparser.parse(day)
        if query_date is None:
            device.log.error(f'Could not parse date query: {day}')
            return f"Could not parse date query: {day}"

        notes = []
        if not os.path.exists(self.config['notes_file']):
            return "No notes file found"
        
        try:
            with open(self.config['notes_file'], 'r') as file:
                for line in file:
                    note_obj = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(note_obj['timestamp'])
                    if timestamp.date() == query_date.date():
                        notes.append(f"{timestamp.strftime('%I:%M %p')} {note_obj['note']}")
            
            if notes:
                return f"Found {len(notes)} notes:\n" + '\n'.join(notes)
            else:
                return f"No notes found for {day}"
                
        except Exception as e:
            device.log.error(f"Error reading notes file: {e}")
            return f"Error reading notes file: {str(e)}"
    
    def control_light(self, device, entity_id, rgb_color=None, brightness=None):
        """Control lights in Home Assistant."""
        with open("credentials.json", "r") as f:
            cred = json.load(f)
        
        HA_TOKEN = cred.get("home_assistant_token")
        HA_URL = cred.get("home_assistant_url")

        params = {"entity_id": entity_id}
        if rgb_color:
            params['rgb_color'] = rgb_color
        if brightness is not None:
            params['brightness'] = brightness

        url = f"{HA_URL}api/services/light/turn_on"
        ha_headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "content-type": "application/json"
        }
        
        try:
            device.log.info(f"Light control request:\n{params}")
            response = requests.post(url, headers=ha_headers, json=params)
            
            if response.status_code == 200:
                device.log.info(f"Light control success")
                return "Success"
            else:
                device.log.error(f"Light control error: {response.status_code} {response.text}")
                return f"Error: {response.status_code} {response.text}"
        except Exception as e:
            device.log.error(f"Error controlling lights: {e}")
            return f"Error controlling lights: {str(e)}"
    
    def control_fan(self, device, entity_id, state):
        """Control fan switches in Home Assistant."""
        with open("credentials.json", "r") as f:
            cred = json.load(f)
        
        HA_TOKEN = cred.get("home_assistant_token")
        HA_URL = cred.get("home_assistant_url")

        # Determine the service to call based on the state
        service = "turn_on" if state == "on" else "turn_off"
        
        url = f"{HA_URL}api/services/switch/{service}"
        ha_headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "content-type": "application/json"
        }
        
        params = {"entity_id": entity_id}
        
        try:
            device.log.info(f"Fan control request: {entity_id} -> {state}")
            response = requests.post(url, headers=ha_headers, json=params)
            
            if response.status_code == 200:
                device.log.info(f"Fan control success")
                return "Success"
            else:
                device.log.error(f"Fan control error: {response.status_code} {response.text}")
                return f"Error: {response.status_code} {response.text}"
        except Exception as e:
            device.log.error(f"Error controlling fan: {e}")
            return f"Error controlling fan: {str(e)}"

    def ask_kobold(self, device, user_input):
        """Main function to get a response from KoboldCPP."""
        # Build the prompt
        full_prompt, conversation_part = self.build_prompt(device, user_input)
        
        # Generate response from KoboldCPP
        generated_text = self.generate_response(device, full_prompt)
        
        # Update the context history for next interaction
        device.context_history = conversation_part + generated_text + "\n"
        
        # Make sure we don't exceed the context window
        max_context_history = self.config.get('kobold', {}).get('max_history_tokens', 1000)
        if len(device.context_history) > max_context_history:
            # Simple token estimation (not accurate but good enough)
            tokens = device.context_history.split()
            if len(tokens) > max_context_history:
                # Trim to approximately keep the most recent conversation
                device.context_history = " ".join(tokens[-max_context_history:])
        
        # Parse the response
        spoken_response, function_calls = self.parse_response(generated_text)
        
        # Combine spoken response with function calls in the same format as LLM output
        full_response = spoken_response
        for fc in function_calls:
            full_response += f"\n<functioncall> {json.dumps(fc)}"

        # Execute any function calls
        function_results = self.execute_functions(device, function_calls)
        
        # Add to message history (for compatibility with existing code)
        device.add_message({"role": "user", "content": user_input})
        device.add_message({"role": "assistant", "content": full_response})
        
        return spoken_response