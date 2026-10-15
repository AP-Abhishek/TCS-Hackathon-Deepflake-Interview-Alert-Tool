"""
ui/hud.py
---------
Responsible: Person 5 (UI/UX - OpenCV Proctoring HUD Overlay)

TASK OBJECTIVE:
- Draw a sleek, high-tech HUD overlay directly onto the OpenCV camera frame.
- Display:
  1. Top Banner: Current Question Text & Question Counter (e.g. "Q 1/3").
  2. Side Card / Status Panel:
     - Real-time Integrity Score Bar (Green 85-100%, Yellow 65-84%, Red <65%).
     - Gaze Direction Badge (CENTER, LOOKING_LEFT, LOOKING_RIGHT).
     - Lip Movement Indicator (TALKING / STATIC / WHISPERING).
     - Face Count Indicator.
     - Mic Volume meter / status.
  3. Warning Toasts / Banners at bottom if an anomaly is active (e.g. "[!] LOOKING OFF-SCREEN").

TODO for Person 5:
1. Implement `draw_hud(frame, interview_state, proctor_state) -> frame`.
2. Add semi-transparent background boxes using cv2.addWeighted for a modern look.
3. Add text wrapping for long questions so they don't clip off the screen.
"""

import cv2
import numpy as np


class ProctorHUD:
    def __init__(self):
        pass

    def draw_hud(self, frame: np.ndarray, interview_state: dict, proctor_state: dict) -> np.ndarray:
        """
        TODO:
        - Read interview_state:
            - question_idx: int
            - total_questions: int
            - current_question: str
            - time_remaining: int
        - Read proctor_state:
            - score: int (0 - 100)
            - gaze_direction: str
            - lip_status: str
            - active_alerts: list of str
        - Render stylish HUD on `frame` and return the modified frame.
        """
        # Placeholder minimal text overlay until Person 5 styles it:
        score = proctor_state.get("score", 100)
        q_text = interview_state.get("current_question", "Ready...")
        cv2.putText(frame, f"Integrity: {score}%", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Question: {q_text[:60]}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        alerts = proctor_state.get("active_alerts", [])
        if alerts:
            cv2.putText(frame, f"ALERT: {alerts[0]}", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return frame
