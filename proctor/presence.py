"""
proctor/presence.py
-------------------
Responsible: Person 1 (Computer Vision - Face Presence & Multi-Person Detection)

TASK OBJECTIVE:
- Monitor the number of faces detected in the camera frame.
- Detect when candidate leaves the screen (0 faces for >= missing_alert_sec).
- Detect when multiple people are in the room (> 1 faces detected).

TODO for Person 1:
1. Accept `num_faces` (integer count from MediaPipe Face Mesh or Face Detection).
2. If num_faces == 0:
   - Accumulate `missing_duration`.
   - If missing_duration >= missing_alert_sec, set is_missing = True.
3. If num_faces > 1:
   - Set is_multiple = True immediately (critical violation).
4. If num_faces == 1:
   - Reset missing timer.
5. Return dictionary matching the exact contract below.
"""

import time


class PresenceTracker:
    def __init__(self, missing_alert_sec: float = 2.5):
        """
        TODO:
        - Store missing alert threshold.
        - Initialize timers.
        """
        self.missing_alert_sec = missing_alert_sec
        self.missing_start_time = None
        self.missing_duration = 0.0

    def update(self, num_faces: int) -> dict:
        """
        TODO:
        - Evaluate face count and update absence timers.

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "face_count": int,         # Total faces detected in current frame
            "is_missing": bool,        # True if 0 faces for >= missing_alert_sec
            "is_multiple": bool,       # True if > 1 faces detected
            "duration_missing": float  # Seconds absent
        }
        """
        now = time.time()
        is_missing = False
        is_multiple = num_faces > 1

        if num_faces == 0:
            if self.missing_start_time is None:
                self.missing_start_time = now
            self.missing_duration = now - self.missing_start_time
            if self.missing_duration >= self.missing_alert_sec:
                is_missing = True
        else:
            self.missing_start_time = None
            self.missing_duration = 0.0
            is_missing = False

        return {
            "face_count": num_faces,
            "is_missing": is_missing,
            "is_multiple": is_multiple,
            "duration_missing": round(self.missing_duration, 1)
        }
