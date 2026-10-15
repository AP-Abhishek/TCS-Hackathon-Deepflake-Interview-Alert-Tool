"""
config.py
---------
Shared Configuration & Thresholds for AI Proctoring System.

TASK OBJECTIVE:
- Load API keys from environment or .env file.
- Define default proctoring thresholds for gaze, lip movement, audio, and presence.
- Define camera and UI resolution settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")


def get_gemini_api_key() -> str:
    """Retrieves the Gemini API key from environment variable or raw .env line."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        env_path = BASE_DIR / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line:
                    key = first_line.split("=", 1)[1].strip() if "=" in first_line else first_line
    return key or ""


GEMINI_API_KEY = get_gemini_api_key()

# ----------------- PROCTORING THRESHOLDS -----------------
# Gaze thresholds (Iris horizontal ratio relative to eye corners)
GAZE_LEFT_RATIO = 0.35
GAZE_RIGHT_RATIO = 0.65
GAZE_AWAY_ALERT_SEC = 2.0  # Seconds looking away before triggering alert

# Lip movement thresholds (Mouth Aspect Ratio - MAR)
MAR_TALKING_THRESHOLD = 0.05
MAR_SILENT_THRESHOLD = 0.02
WHISPER_WINDOW_SEC = 2.5   # Continuous lip movement with silent mic

# Audio energy thresholds
AUDIO_SPEECH_THRESHOLD = 0.015  # RMS amplitude threshold for speech detection

# Presence thresholds
FACE_MISSING_ALERT_SEC = 2.5

# ----------------- CAMERA & UI SETTINGS -----------------
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
QUESTION_TIME_LIMIT_SEC = 45
