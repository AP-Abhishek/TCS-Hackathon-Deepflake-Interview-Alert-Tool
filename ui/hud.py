"""
ui/hud.py
---------
Responsible: Person 5 (UI/UX - OpenCV Proctoring HUD Overlay)

TASK DELIVERABLE:
- Modern Sci-Fi / Glassmorphic HUD overlay for OpenCV camera frame.
- Displays question prompt, countdown timer, live integrity score bar,
  telemetry badges (Gaze, Lips, Audio, Presence), and high-visibility alert toasts.
"""

import cv2
import numpy as np


class ProctorHUD:
    def __init__(self):
        # Color Palette (BGR format for OpenCV)
        self.COLOR_BG = (18, 22, 28)           # Dark Navy/Slate
        self.COLOR_PANEL = (26, 32, 44)        # Card Background
        self.COLOR_BORDER = (45, 55, 72)       # Card Border
        self.COLOR_PRIMARY = (255, 170, 0)     # Cyan/Blue Accent
        self.COLOR_GREEN = (72, 201, 74)       # Clean / Good (Green)
        self.COLOR_AMBER = (0, 191, 255)       # Suspicious / Warning (Gold/Amber)
        self.COLOR_RED = (60, 60, 240)         # High Risk / Alert (Red)
        self.COLOR_WHITE = (245, 245, 245)
        self.COLOR_MUTED = (160, 174, 192)

    def draw_glass_panel(self, frame: np.ndarray, x: int, y: int, w: int, h: int, 
                         bg_color=None, alpha: float = 0.75, border_color=None) -> np.ndarray:
        """Draws a semi-transparent glassmorphic background box with border."""
        if bg_color is None:
            bg_color = self.COLOR_PANEL
        if border_color is None:
            border_color = self.COLOR_BORDER

        frame_h, frame_w = frame.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(frame_w, x + w), min(frame_h, y + h)

        if x2 <= x1 or y2 <= y1:
            return frame

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, 1, cv2.LINE_AA)
        return frame

    def wrap_text(self, text: str, max_chars_per_line: int = 68) -> list:
        """Splits long question strings into wrapped lines for clean display."""
        words = text.split(" ")
        lines = []
        current_line = []
        current_len = 0

        for word in words:
            if current_len + len(word) + 1 > max_chars_per_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = len(word)
            else:
                current_line.append(word)
                current_len += len(word) + 1

        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def draw_hud(self, frame: np.ndarray, interview_state: dict, proctor_state: dict) -> np.ndarray:
        """
        Renders the full high-tech proctoring HUD over the video frame.

        interview_state keys:
            - question_idx: int (1-based)
            - total_questions: int
            - current_question: str
            - time_remaining: int (seconds)
            - is_finished: bool

        proctor_state keys:
            - score: int (0 - 100)
            - status: str ('CLEAN', 'SUSPICIOUS', 'HIGH_RISK')
            - gaze_direction: str ('CENTER', 'LOOKING_LEFT', 'LOOKING_RIGHT', etc.)
            - is_gaze_away: bool
            - lip_status: str ('TALKING', 'STATIC', 'WHISPERING')
            - mar: float
            - audio_speaking: bool
            - audio_volume: float
            - face_count: int
            - active_alerts: list of str
        """
        frame_h, frame_w = frame.shape[:2]

        # ---------------- 1. TOP HEADER & QUESTION CARD ----------------
        q_idx = interview_state.get("question_idx", 1)
        total_q = interview_state.get("total_questions", 3)
        question_text = interview_state.get("current_question", "Loading question...")
        time_left = max(0, interview_state.get("time_remaining", 45))
        is_finished = interview_state.get("is_finished", False)

        # Draw top banner panel (Width: frame_w - 380 to leave room for right telemetry)
        q_panel_w = frame_w - 360
        self.draw_glass_panel(frame, 20, 15, q_panel_w, 110, alpha=0.82)

        # Header subtext
        header_tag = f"AI PROCTOR INTELLIGENCE  //  QUESTION {q_idx} OF {total_q}"
        cv2.putText(frame, header_tag, (35, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_PRIMARY, 1, cv2.LINE_AA)

        # Timer Badge
        timer_text = f"TIME: {time_left:02d}s"
        timer_color = self.COLOR_GREEN if time_left > 15 else (self.COLOR_AMBER if time_left > 5 else self.COLOR_RED)
        cv2.putText(frame, timer_text, (q_panel_w - 110, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, timer_color, 2, cv2.LINE_AA)

        # Wrapped Question Text
        lines = self.wrap_text(question_text, max_chars_per_line=62)
        y_offset = 65
        for line in lines[:2]: # Show up to 2 lines cleanly
            cv2.putText(frame, line, (35, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.COLOR_WHITE, 1, cv2.LINE_AA)
            y_offset += 24

        # ---------------- 2. RIGHT TELEMETRY & INTEGRITY PANEL ----------------
        panel_x = frame_w - 325
        panel_y = 15
        panel_w = 305
        panel_h = 360

        self.draw_glass_panel(frame, panel_x, panel_y, panel_w, panel_h, alpha=0.85)

        # Panel Title
        cv2.putText(frame, "CANDIDATE TELEMETRY", (panel_x + 15, panel_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_PRIMARY, 1, cv2.LINE_AA)

        # 2a. Integrity Score Progress Bar
        score = max(0, min(100, proctor_state.get("score", 100)))
        status = proctor_state.get("status", "CLEAN")

        if score >= 85:
            score_color = self.COLOR_GREEN
        elif score >= 65:
            score_color = self.COLOR_AMBER
        else:
            score_color = self.COLOR_RED

        cv2.putText(frame, "INTEGRITY SCORE", (panel_x + 15, panel_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.COLOR_MUTED, 1, cv2.LINE_AA)

        score_display = f"{score}% [{status}]"
        cv2.putText(frame, score_display, (panel_x + 175, panel_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, score_color, 2, cv2.LINE_AA)

        # Progress Bar
        bar_x = panel_x + 15
        bar_y = panel_y + 70
        bar_w = panel_w - 30
        bar_h = 10
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (40, 48, 60), -1)
        fill_w = int(bar_w * (score / 100.0))
        if fill_w > 0:
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), score_color, -1)

        # Separator line
        cv2.line(frame, (panel_x + 15, panel_y + 95), (panel_x + panel_w - 15, panel_y + 95), self.COLOR_BORDER, 1)

        # 2b. Gaze Direction
        gaze_dir = proctor_state.get("gaze_direction", "CENTER")
        is_away = proctor_state.get("is_gaze_away", False)
        gaze_color = self.COLOR_RED if is_away else self.COLOR_GREEN

        cv2.putText(frame, "EYE GAZE:", (panel_x + 15, panel_y + 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(frame, gaze_dir, (panel_x + 130, panel_y + 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, gaze_color, 1, cv2.LINE_AA)

        # 2c. Lip Dynamics / MAR
        lip_status = proctor_state.get("lip_status", "STATIC")
        mar_val = proctor_state.get("mar", 0.0)
        lip_color = self.COLOR_GREEN if lip_status == "TALKING" else self.COLOR_WHITE
        if "WHISPER" in lip_status:
            lip_color = self.COLOR_AMBER

        cv2.putText(frame, "LIP DYNAMICS:", (panel_x + 15, panel_y + 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(frame, f"{lip_status} ({mar_val:.2f})", (panel_x + 130, panel_y + 165),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, lip_color, 1, cv2.LINE_AA)

        # 2d. Audio Speech Activity
        audio_speaking = proctor_state.get("audio_speaking", False)
        audio_color = self.COLOR_GREEN if audio_speaking else self.COLOR_MUTED
        audio_label = "ACTIVE SPEECH" if audio_speaking else "AMBIENT SILENCE"

        cv2.putText(frame, "AUDIO INPUT:", (panel_x + 15, panel_y + 205),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(frame, audio_label, (panel_x + 130, panel_y + 205),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, audio_color, 1, cv2.LINE_AA)

        # 2e. Face Presence Count
        face_count = proctor_state.get("face_count", 1)
        if face_count == 1:
            presence_label = "1 Verified Face"
            presence_color = self.COLOR_GREEN
        elif face_count == 0:
            presence_label = "0 FACES (ABSENT)"
            presence_color = self.COLOR_RED
        else:
            presence_label = f"{face_count} FACES (MULTIPLE!)"
            presence_color = self.COLOR_RED

        cv2.putText(frame, "PRESENCE:", (panel_x + 15, panel_y + 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(frame, presence_label, (panel_x + 130, panel_y + 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, presence_color, 1, cv2.LINE_AA)

        # 2f. Total Infractions Count
        infraction_count = proctor_state.get("infractions_count", 0)
        cv2.putText(frame, "INFRACTIONS:", (panel_x + 15, panel_y + 285),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_MUTED, 1, cv2.LINE_AA)
        cv2.putText(frame, f"{infraction_count} LOGGED", (panel_x + 130, panel_y + 285),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, self.COLOR_WHITE if infraction_count == 0 else self.COLOR_AMBER, 1, cv2.LINE_AA)

        # System Status Footer inside Card
        cv2.line(frame, (panel_x + 15, panel_y + 310), (panel_x + panel_w - 15, panel_y + 310), self.COLOR_BORDER, 1)
        cv2.putText(frame, "AI ENGINE: ACTIVE MONITORING", (panel_x + 25, panel_y + 335),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, self.COLOR_PRIMARY, 1, cv2.LINE_AA)

        # ---------------- 3. BOTTOM ACTIVE ALERTS TOAST ----------------
        active_alerts = proctor_state.get("active_alerts", [])
        if active_alerts:
            toast_text = f"[!] {active_alerts[0]}"
            toast_w = max(400, len(toast_text) * 14)
            toast_x = max(20, (frame_w - toast_w) // 2)
            toast_y = frame_h - 90

            # Red warning toast with high opacity
            self.draw_glass_panel(frame, toast_x, toast_y, toast_w, 42,
                                  bg_color=(20, 20, 180), alpha=0.9, border_color=(80, 80, 255))
            cv2.putText(frame, toast_text, (toast_x + 20, toast_y + 27),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_WHITE, 2, cv2.LINE_AA)

        # ---------------- 4. BOTTOM KEYBOARD SHORTCUTS BAR ----------------
        bottom_bar = "[N] Next Question   |   [Q] Finish & Generate Report"
        cv2.putText(frame, bottom_bar, (30, frame_h - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_MUTED, 1, cv2.LINE_AA)

        # ---------------- 5. FINAL INTERVIEW COMPLETED OVERLAY ----------------
        if is_finished:
            modal_w = 640
            modal_h = 320
            modal_x = (frame_w - modal_w) // 2
            modal_y = (frame_h - modal_h) // 2

            self.draw_glass_panel(frame, modal_x, modal_y, modal_w, modal_h,
                                  bg_color=(12, 16, 22), alpha=0.95, border_color=score_color)

            cv2.putText(frame, "INTERVIEW SESSION CONCLUDED", (modal_x + 130, modal_y + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_PRIMARY, 2, cv2.LINE_AA)

            final_label = f"Final Integrity Score: {score}% ({status})"
            cv2.putText(frame, final_label, (modal_x + 150, modal_y + 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2, cv2.LINE_AA)

            inf_label = f"Total Proctoring Infractions Flagged: {infraction_count}"
            cv2.putText(frame, inf_label, (modal_x + 130, modal_y + 175),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.COLOR_WHITE, 1, cv2.LINE_AA)

            decision = "RECOMMENDATION: VERIFIED & TRUSTED" if score >= 80 else "RECOMMENDATION: REQUIRES HUMAN REVIEW"
            dec_color = self.COLOR_GREEN if score >= 80 else self.COLOR_AMBER
            cv2.putText(frame, decision, (modal_x + 120, modal_y + 225),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, dec_color, 2, cv2.LINE_AA)

            cv2.putText(frame, "Press 'Q' to save audit report and exit.", (modal_x + 160, modal_y + 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_MUTED, 1, cv2.LINE_AA)

        return frame
