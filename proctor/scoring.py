"""
proctor/scoring.py
------------------
Responsible: Person 4 (Cheating Scoring, Heuristics & Reports)

TASK OBJECTIVE:
- Ingest proctoring data from Gaze, Lips, Audio, and Presence modules.
- Evaluate cheating heuristics (multiple people, missing face, off-screen gaze, whispering, proxy speech).
- Maintain dynamic Integrity Score (starts at 100%, degrades upon infractions).
- Record timestamped infractions for the final audit report.

TODO for Person 4:
1. Deduct score when violations occur:
   - Presence: Multiple faces (-0.4 per frame or immediate flag), Missing face (-0.25 per frame).
   - Gaze: Looking away for sustained time (-0.15 per frame).
   - Audio-Visual Discrepancy:
     * Whispering (Lips moving + Audio silent for > 2.0s) -> -0.2 per frame.
     * External Prompter (Audio speaking + Lips static for > 1.5s) -> -0.3 per frame.
2. Maintain active_alerts list for the HUD toaster.
3. Log unique infractions to `self.infractions` with timestamp and penalty reason.
4. Classify status: "CLEAN" (>= 85%), "SUSPICIOUS" (65 - 84%), "HIGH_RISK" (< 65%).
5. Return dictionary matching the exact contract below.
"""

import time
from datetime import datetime


class IntegrityScorer:
    def __init__(self, initial_score: float = 100.0):
        """
        TODO:
        - Initialize starting score (100.0).
        - Initialize infractions list.
        - Initialize debounce timers.
        """
        self.score = initial_score
        self.infractions = []
        self.last_penalty_time = 0.0
        self.last_infraction_times = {}
        self.whisper_start_time = None
        self.external_voice_start_time = None

    def evaluate(self, gaze_data: dict, lip_data: dict, audio_data: dict, presence_data: dict) -> dict:
        """
        TODO:
        - Ingest signals:
            - gaze_data: {"direction": str, "is_away": bool, "duration": float}
            - lip_data: {"mar": float, "is_moving": bool, "duration": float}
            - audio_data: {"volume": float, "is_speaking": bool}
            - presence_data: {"face_count": int, "is_missing": bool, "is_multiple": bool}
        - Apply cross-modal heuristic rules.
        - Deduct score penalties.
        - Assemble active_alerts list.

        RETURN CONTRACT (DO NOT CHANGE KEYS):
        {
            "score": int,              # Current integrity score (0 - 100)
            "status": str,             # 'CLEAN', 'SUSPICIOUS', or 'HIGH_RISK'
            "active_alerts": list,     # List of active warning strings for HUD
            "infractions_count": int   # Total logged infractions so far
        }
        """
        now = time.time()
        active_alerts = []
        current_penalty = 0.0

        # 1. Presence Anomaly Checks
        if presence_data.get("is_multiple"):
            active_alerts.append("CRITICAL: MULTIPLE PERSONS DETECTED")
            current_penalty += 0.4
            self._log_infraction("Multiple persons detected in camera")
        elif presence_data.get("is_missing"):
            active_alerts.append(f"WARNING: CANDIDATE MISSING ({presence_data.get('duration_missing', 0)}s)")
            current_penalty += 0.25
            self._log_infraction("Candidate absent from camera frame")

        # 2. Gaze Anomaly Checks
        if gaze_data.get("is_away"):
            active_alerts.append(f"FLAG: LOOKING OFF-SCREEN ({gaze_data.get('direction')})")
            current_penalty += 0.15
            self._log_infraction(f"Off-screen gaze: {gaze_data.get('direction')}")

        # 3. Audio-Visual Cross-Modal Checks
        is_lip_moving = lip_data.get("is_moving", False)
        is_audio_speaking = audio_data.get("is_speaking", False)

        # 3a. Whispering: Lips moving without detected speech
        if is_lip_moving and not is_audio_speaking:
            if self.whisper_start_time is None:
                self.whisper_start_time = now
            whisper_duration = now - self.whisper_start_time
            if whisper_duration >= 2.0:
                active_alerts.append(f"FLAG: SILENT LIP MOVEMENT / WHISPERING ({round(whisper_duration, 1)}s)")
                current_penalty += 0.2
                self._log_infraction("Candidate moving lips without detected speech (Whispering)")
        else:
            self.whisper_start_time = None

        # 3b. External Prompter: Audio detected while lips remain closed
        if is_audio_speaking and not is_lip_moving:
            if self.external_voice_start_time is None:
                self.external_voice_start_time = now
            ext_duration = now - self.external_voice_start_time
            if ext_duration >= 1.5:
                active_alerts.append("FLAG: EXTERNAL VOICE DETECTED (LIPS STATIC)")
                current_penalty += 0.3
                self._log_infraction("Speech detected while candidate lips are closed (Possible proxy/prompter)")
        else:
            self.external_voice_start_time = None

        # Apply score penalty
        self.score = max(0.0, self.score - current_penalty)

        # Classification
        if self.score >= 85:
            status = "CLEAN"
        elif self.score >= 65:
            status = "SUSPICIOUS"
        else:
            status = "HIGH_RISK"

        return {
            "score": int(round(self.score)),
            "status": status,
            "active_alerts": active_alerts,
            "infractions_count": len(self.infractions)
        }

    def _log_infraction(self, description: str, cooldown_sec: float = 3.0):
        """Debounces and records unique timestamped infractions."""
        now = time.time()
        last_time = self.last_infraction_times.get(description, 0.0)
        if now - last_time < cooldown_sec:
            return

        self.last_infraction_times[description] = now
        self.last_penalty_time = now
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.infractions.append({
            "timestamp": timestamp,
            "type": description,
            "score_at_time": int(round(self.score))
        })

    def get_summary(self) -> dict:
        """
        TODO:
        - Return the final proctoring summary report.
        """
        return {
            "final_score": int(round(self.score)),
            "total_infractions": len(self.infractions),
            "infractions_log": self.infractions
        }
