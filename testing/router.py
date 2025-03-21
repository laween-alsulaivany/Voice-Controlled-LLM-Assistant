# router.py
"""
Decides whether the transcribed text should go to Home Assistant or the LLM.
"""

# TODO: this method is very basic and can be improved
KEYWORDS_HA = ["turn on", "turn off", "lights",
               "thermostat", "fan", "kitchen", "bedroom"]


def is_ha_command(text: str) -> bool:
    """
    Basic keyword-based approach:
    If the text contains certain home automation keywords, we assume it's a HA command.
    """
    text_lower = text.lower()
    for kw in KEYWORDS_HA:
        if kw in text_lower:
            return True
    return False


def route_command(transcribed_text: str) -> str:
    """
    Returns 'HA' or 'LLM' depending on whether the text
    should go to Home Assistant or the local LLM.
    """
    if is_ha_command(transcribed_text):
        return "HA"
    else:
        return "LLM"
