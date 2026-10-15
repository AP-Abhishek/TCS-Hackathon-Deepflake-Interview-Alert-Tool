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
        Extract lip points: Upper=13, Lower=14, Left=61, Right=291.
        Calculate vertical Euclidean distance / horizontal Euclidean distance.
        Return float MAR.
        """
        try:
            # Extract landmark coordinates and scale to pixel space
            upper_lip = np.array([landmarks[13].x * frame_w, landmarks[13].y * frame_h])
            lower_lip = np.array([landmarks[14].x * frame_w, landmarks[14].y * frame_h])
            left_corner = np.array([landmarks[61].x * frame_w, landmarks[61].y * frame_h])
            right_corner = np.array([landmarks[291].x * frame_w, landmarks[291].y * frame_h])

            # Vertical distance (lip opening)
            vertical_dist = np.linalg.norm(upper_lip - lower_lip)

            # Horizontal distance (mouth width)
            horizontal_dist = np.linalg.norm(left_corner - right_corner)

            if horizontal_dist < 1e-6:
                return 0.0

            return float(vertical_dist / horizontal_dist)
        except (IndexError, AttributeError):
            return 0.0

    def update(self, landmarks, frame_w: int, frame_h: int) -> dict:
        """
        Compute current frame MAR.
        If MAR > talking_threshold: is_moving = True, accumulate movement_duration.
        Else: is_moving = False, reset movement_duration.

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "mar": float,          # Current frame Mouth Aspect Ratio
            "is_moving": bool,     # True if candidate is moving mouth
            "duration": float      # Seconds mouth has been continuously moving
        }
        """
        now = time.time()
        mar = self.compute_mar(landmarks, frame_w, frame_h)

        if mar > self.talking_threshold:
            if not self.is_moving:
                # Mouth just started moving — record start time
                self.lip_moving_start_time = now
                self.is_moving = True
            self.movement_duration = now - self.lip_moving_start_time
        else:
            # Mouth is closed/static — reset tracking
            self.is_moving = False
            self.lip_moving_start_time = None
            self.movement_duration = 0.0

        return {
            "mar": round(mar, 4),
            "is_moving": self.is_moving,
            "duration": round(self.movement_duration, 1)
        }
