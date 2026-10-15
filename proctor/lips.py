"""
proctor/lips.py
---------------
Responsible: Person 2 (Lip Dynamics & Mouth Aspect Ratio - MAR)

TASK OBJECTIVE:
- Calculate Mouth Aspect Ratio (MAR) using MediaPipe inner lip landmarks.
- Determine whether the candidate is actively speaking, silent, or whispering.
- Track duration of continuous mouth movements.

LANDMARK REFERENCES (MediaPipe Face Mesh):
- Left corner of mouth: 61
- Right corner of mouth: 291
- Upper inner lip: 13
- Lower inner lip: 14

FORMULA:
  MAR = Distance(UpperLip[13], LowerLip[14]) / Distance(LeftCorner[61], RightCorner[291])

TODO for Person 2:
1. Extract (x, y) coordinates of lip landmarks from 478 points.
2. Compute vertical distance between inner lips (landmarks 13 & 14).
3. Compute horizontal distance between mouth corners (landmarks 61 & 291).
4. Compute MAR = vertical_distance / horizontal_distance.
5. If MAR > talking_threshold, set is_moving = True and accumulate movement_duration.
6. Return dictionary matching the exact contract below.
"""

import time
import numpy as np


class LipTracker:
    def __init__(self, talking_threshold: float = 0.05, whisper_window_sec: float = 2.5):
        """
        TODO:
        - Store MAR threshold for speaking activity.
        - Initialize timers and movement tracking variables.
        """
        self.talking_threshold = talking_threshold
        self.whisper_window_sec = whisper_window_sec
        self.lip_moving_start_time = None
        self.is_moving = False
        self.movement_duration = 0.0

    def compute_mar(self, landmarks, frame_w: int, frame_h: int) -> float:
        """
        TODO:
        - Extract lip points: Upper=13, Lower=14, Left=61, Right=291.
        - Calculate vertical Euclidean distance / horizontal Euclidean distance.
        - Return float MAR.
        """
        # Placeholder skeleton until Person 2 fills in:
        return 0.0

    def update(self, landmarks, frame_w: int, frame_h: int) -> dict:
        """
        TODO:
        - Compute current frame MAR.
        - If MAR > talking_threshold:
            - is_moving = True
            - accumulate movement_duration
        - Else:
            - is_moving = False
            - reset movement_duration

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "mar": float,          # Current frame Mouth Aspect Ratio
            "is_moving": bool,     # True if candidate is moving mouth
            "duration": float      # Seconds mouth has been continuously moving
        }
        """
        # Placeholder skeleton until Person 2 implements:
        return {
            "mar": 0.0,
            "is_moving": self.is_moving,
            "duration": round(self.movement_duration, 1)
        }
