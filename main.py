"""
main.py
-------
Responsible: Person 5 & Project Integrator (Main Orchestrator & CLI Entrypoint)

TASK OBJECTIVE:
- Parse CLI arguments (e.g. `python main.py --skills "Python, ML" --questions 3`).
- Connect all modular components:
  1. AI Question Engine (interview/ai_agent.py)
  2. Agent Speaker (interview/speaker.py)
  3. Gaze & Iris Tracker (proctor/gaze.py)
  4. Lip Dynamics (proctor/lips.py)
  5. Audio Monitor (proctor/audio.py)
  6. Face Presence (proctor/presence.py)
  7. Integrity Scorer (proctor/scoring.py)
  8. HUD Renderer (ui/hud.py)
  9. Report Generator (reports/generator.py)
- Run the real-time OpenCV webcam loop with 'q' to quit and 'n' to go to next question.

TODO for Integrator / Person 5:
1. Parse CLI arguments using argparse.
2. Initialize MediaPipe Face Mesh.
3. In the webcam loop, feed landmarks to trackers and draw HUD.
4. Manage interview state (current question timer, advancing questions).
5. Trigger report generation when interview finishes.
"""

import argparse
import time
import cv2
import mediapipe as mp

import config
from interview.ai_agent import AIInterviewAgent
from interview.speaker import AgentSpeaker
from proctor.gaze import GazeTracker
from proctor.lips import LipTracker
from proctor.audio import AudioMonitor
from proctor.presence import PresenceTracker
from proctor.scoring import IntegrityScorer
from ui.hud import ProctorHUD
from reports.generator import save_report


def parse_args():
    parser = argparse.ArgumentParser(description="AI Proctoring & Technical Interview Platform")
    parser.add_argument("--skills", type=str, default="Python, Machine Learning", help="Comma-separated skills to test")
    parser.add_argument("--questions", type=int, default=3, help="Number of interview questions to ask")
    return parser.parse_args()


def main():
    args = parse_args()
    skills_list = [s.strip() for s in args.skills.split(",") if s.strip()]

    print("==================================================")
    print("  AI PROCTORED INTERVIEW PLATFORM - PROTOTYPE")
    print(f"  Target Skills: {skills_list}")
    print(f"  Questions: {args.questions}")
    print("==================================================")

    # 1. Initialize Subsystems
    # TODO: Load questions via AIInterviewAgent
    # agent = AIInterviewAgent()
    # questions = agent.generate_questions(skills_list, args.questions)

    # 2. Initialize Trackers & HUD
    # gaze_tracker = GazeTracker(config.GAZE_AWAY_ALERT_SEC)
    # lip_tracker = LipTracker(config.MAR_TALKING_THRESHOLD)
    # audio_monitor = AudioMonitor()
    # audio_monitor.start()
    # presence_tracker = PresenceTracker()
    # scorer = IntegrityScorer()
    # hud = ProctorHUD()

    # 3. Main OpenCV Capture Loop
    # cap = cv2.VideoCapture(config.CAMERA_INDEX)
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret: break
    #     ... process landmarks & draw HUD ...
    #     if cv2.waitKey(1) & 0xFF == ord('q'): break

    print("[Main] Scaffold ready. Distribute tasks to your team.")


if __name__ == "__main__":
    main()
