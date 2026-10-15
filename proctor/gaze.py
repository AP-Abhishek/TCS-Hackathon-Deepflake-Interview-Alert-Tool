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
        Calculate horizontal position of iris relative to the eye corners.
        Returns float ratio between 0.0 and 1.0 (0.0 = full left, 1.0 = full right).
        """
        # Ensure corner_left has smaller x coordinate
        if corner_left[0] > corner_right[0]:
            corner_left, corner_right = corner_right, corner_left

        eye_width = corner_right[0] - corner_left[0]
        if eye_width < 1e-4:
            return 0.5

        dist_from_left = iris_pt[0] - corner_left[0]
        ratio = float(dist_from_left / eye_width)
        return float(np.clip(ratio, 0.0, 1.0))

    def update(self, landmarks, frame_w: int, frame_h: int) -> dict:
        """
        Receive MediaPipe landmarks and compute gaze direction & away duration.

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "direction": str,       # 'CENTER', 'LOOKING_LEFT', 'LOOKING_RIGHT'
            "is_away": bool,        # True if candidate is looking away for >= away_alert_sec
            "duration": float,      # Duration looking away in seconds
            "left_ratio": float,    # 0.0 to 1.0
            "right_ratio": float    # 0.0 to 1.0
        }
        """
        now = time.time()

        try:
            # Extract Left Eye: Corner 33, Corner 133, Iris 468
            l_c1 = np.array([landmarks[33].x * frame_w, landmarks[33].y * frame_h])
            l_c2 = np.array([landmarks[133].x * frame_w, landmarks[133].y * frame_h])
            l_iris = np.array([landmarks[468].x * frame_w, landmarks[468].y * frame_h])

            # Extract Right Eye: Corner 362, Corner 263, Iris 473
            r_c1 = np.array([landmarks[362].x * frame_w, landmarks[362].y * frame_h])
            r_c2 = np.array([landmarks[263].x * frame_w, landmarks[263].y * frame_h])
            r_iris = np.array([landmarks[473].x * frame_w, landmarks[473].y * frame_h])

            left_ratio = self.calculate_ratio(l_iris, l_c1, l_c2)
            right_ratio = self.calculate_ratio(r_iris, r_c1, r_c2)
            avg_ratio = (left_ratio + right_ratio) / 2.0

            # Direction classification based on horizontal iris position
            if avg_ratio < 0.38:
                self.current_direction = "LOOKING_LEFT"
            elif avg_ratio > 0.62:
                self.current_direction = "LOOKING_RIGHT"
            else:
                self.current_direction = "CENTER"

        except (IndexError, AttributeError):
            left_ratio = 0.5
            right_ratio = 0.5
            self.current_direction = "CENTER"

        # Accumulate away duration if looking off-center
        if self.current_direction != "CENTER":
            if self.gaze_away_start_time is None:
                self.gaze_away_start_time = now
            self.gaze_away_duration = now - self.gaze_away_start_time
            if self.gaze_away_duration >= self.away_alert_sec:
                self.is_gaze_away = True
        else:
            self.gaze_away_start_time = None
            self.gaze_away_duration = 0.0
            self.is_gaze_away = False

        return {
            "direction": self.current_direction,
            "is_away": self.is_gaze_away,
            "duration": round(self.gaze_away_duration, 1),
            "left_ratio": round(left_ratio, 3),
            "right_ratio": round(right_ratio, 3)
        }
