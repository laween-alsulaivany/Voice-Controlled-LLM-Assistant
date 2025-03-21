import requests

HA_BASE_URL = "http://homeassistant.local:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0ZjVkNjhhNDA5ODU0NzlmOWEyMDA5NTJlMzQ4OTlhYiIsImlhdCI6MTc0MjQ0MzE4OCwiZXhwIjoyMDU3ODAzMTg4fQ.vePb9vI5PFB0_yh9NIdBJqVgNyd646d_AF04pOr8DGw"
headers = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}


def send_to_conversation(text):
    url = f"{HA_BASE_URL}/api/conversation/process"
    payload = {"text": text}
    response = requests.post(url, json=payload, headers=headers)

    try:
        # Attempt to parse the response as JSON
        response_data = response.json()
        print(response_data)
    except requests.exceptions.JSONDecodeError:
        # Handle cases where the response is not JSON
        print("Failed to decode JSON response. Raw response:")
        print(response.text)


send_to_conversation("tell me the weather")
