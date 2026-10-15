"""
interview/speaker.py
--------------------
Responsible: Person 3 (AI Interviewer - Text-to-Speech)

TASK OBJECTIVE:
- Convert text questions into spoken audio so the AI Agent speaks to the candidate.
- Run speech in a non-blocking background thread so the OpenCV video window does not freeze!

TODO for Person 3:
1. Initialize pyttsx3 engine.
2. Configure voice properties (rate, volume, voice gender).
3. Implement `speak_async(text)` using threading.Thread so it runs concurrently with OpenCV.
4. Implement `is_speaking()` status flag.
"""

import threading
from typing import Optional


class AgentSpeaker:
    def __init__(self, rate: int = 175, volume: float = 1.0):
        """
        TODO:
        - Initialize pyttsx3 engine.
        - Set speech rate and volume.
        """
        self.rate = rate
        self.volume = volume
        self._is_speaking = False

    def speak_async(self, text: str):
        """
        TODO:
        - Spawn a background thread that invokes pyttsx3.say(text) and pyttsx3.runAndWait().
        - Keep self._is_speaking = True while talking, and False when done.
        """
        pass

    def is_speaking(self) -> bool:
        """Returns True if the AI agent is currently speaking."""
        return self._is_speaking
