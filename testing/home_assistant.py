# home_assistant.py
"""
Provides functions to interact with Home Assistant via the REST API.
"""

import requests
from config import HOME_ASSISTANT_URL, HOME_ASSISTANT_TOKEN


def send_to_ha_conversation(text: str):
    """
    Calls Home Assistant's conversation/process endpoint with the given text.
    Returns JSON response from HA.
    """
    url = f"{HOME_ASSISTANT_URL}/api/conversation/process"
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error from HA conversation:", response.text)
        return None


def simple_test_command():

    resp = send_to_ha_conversation("Turn on the chromecast")
    print("HA Response:", resp)
