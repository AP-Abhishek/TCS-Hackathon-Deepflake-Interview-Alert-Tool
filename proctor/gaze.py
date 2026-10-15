"""
proctor/gaze.py
---------------
Responsible: Person 1 (Computer Vision - Eye & Gaze Tracking)

TASK OBJECTIVE:
- Track left & right iris center landmarks using MediaPipe Face Mesh.
- Compute horizontal and vertical gaze ratios relative to inner and outer eye canthi.
- Detect prolonged off-screen looking (e.g. secondary monitor or phone on desk).

LANDMARK REFERENCES (MediaPipe Face Mesh 478 points):
- Left Eye: Outer canthus = 33, Inner canthus = 133, Iris center = 468
- Right Eye: Inner canthus = 362, Outer canthus = 263, Iris center = 473

TODO for Person 1:
1. Extract (x, y) coordinates for iris centers and eye corners from landmarks.
2. Calculate the horizontal ratio = distance(iris, inner_corner) / eye_width.
3. Classify gaze direction:
   - ratio < 0.35 -> "LOOKING_RIGHT"
   - ratio > 0.65 -> "LOOKING_LEFT"
   - otherwise    -> "CENTER"
4. Track sustained looking away duration (flag is_away=True if away >= away_alert_sec).
5. Return a dictionary with the exact contract below.
"""

import time
import numpy as np


class GazeTracker:
    def __init__(self, away_alert_sec: float = 2.0):
        """
        TODO:
        - Store alert threshold duration.
        - Initialize timers and tracking state variables.
        """
        self.away_alert_sec = away_alert_sec
        self.gaze_away_start_time = None
        self.current_direction = "CENTER"
        self.is_gaze_away = False
        self.gaze_away_duration = 0.0

    def calculate_ratio(self, iris_pt: np.ndarray, corner_left: np.ndarray, corner_right: np.ndarray) -> float:
        """
        TODO:
        - Calculate horizontal distance of iris from corner_left relative to total eye width.
        - Return float ratio between 0.0 and 1.0.
        """
        eye_width = np.linalg.norm(corner_right - corner_left)
        if eye_width < 1e-6:
            return 0.5
        dist_from_left = np.linalg.norm(iris_pt - corner_left)
        return float(dist_from_left / eye_width)

    def update(self, landmarks, frame_w: int, frame_h: int) -> dict:
        """
        TODO:
        - Receive 478 MediaPipe landmarks.
        - Extract left and right iris centers (468, 473) and eye corners.
        - Compute left_ratio and right_ratio.
        - Classify direction ('CENTER', 'LOOKING_LEFT', 'LOOKING_RIGHT').
        - If direction is not 'CENTER', accumulate gaze_away_duration.
        - If duration >= self.away_alert_sec, set is_away = True.

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "direction": str,       # 'CENTER', 'LOOKING_LEFT', 'LOOKING_RIGHT'
            "is_away": bool,        # True if candidate is looking away for >= away_alert_sec
            "duration": float,      # Duration looking away in seconds
            "left_ratio": float,    # 0.0 to 1.0
            "right_ratio": float    # 0.0 to 1.0
        }
        """
        # Placeholder skeleton until Person 1 implements full calculation:
        return {
            "direction": self.current_direction,
            "is_away": self.is_gaze_away,
            "duration": round(self.gaze_away_duration, 1),
            "left_ratio": 0.5,
            "right_ratio": 0.5
        }
