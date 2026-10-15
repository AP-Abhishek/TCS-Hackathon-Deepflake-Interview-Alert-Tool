"""
main.py
-------
Responsible: Person 5 & Integrator (Main Orchestrator & CLI Entrypoint)

Integrates:
- Question Generator (interview/ai_agent.py)
- Voice TTS Speaker (interview/speaker.py)
- Eye & Gaze Tracker (proctor/gaze.py)
- Lip Dynamics (proctor/lips.py)
- Audio Energy Monitor (proctor/audio.py)
- Presence & Multi-face Tracker (proctor/presence.py)
- Integrity Scorer (proctor/scoring.py)
- High-tech HUD Overlay (ui/hud.py)
- Audit Report Saver (reports/generator.py)
"""

import argparse
import sys
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
    parser.add_argument("--skills", type=str, default="Python, Machine Learning, SQL",
                        help="Comma-separated technical skills to test (e.g. 'Python, FastAPI, Docker')")
    parser.add_argument("--questions", type=int, default=3,
                        help="Number of questions to ask during the interview")
    parser.add_argument("--time-per-q", type=int, default=config.QUESTION_TIME_LIMIT_SEC,
                        help="Time limit per question in seconds")
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX,
                        help="Camera device index (default: 0)")
    return parser.parse_args()


def main():
    args = parse_args()
    skills_list = [s.strip() for s in args.skills.split(",") if s.strip()]

    print("\n=======================================================")
    print("      AI PROCTORED INTERVIEW PLATFORM - ACTIVE         ")
    print(f"  Target Skills: {skills_list}")
    print(f"  Question Count: {args.questions}")
    print(f"  Time Per Question: {args.time_per_q}s")
    print("=======================================================\n")

    # 1. Initialize AI Interviewer & TTS Speaker
    print("[1/5] Initializing AI Question Generator...")
    agent = AIInterviewAgent()
    try:
        questions = agent.generate_questions(skills_list, num_questions=args.questions)
    except Exception as e:
        print(f"  Warning: Question generation error ({e}). Using default questions.")
        questions = [
            f"Explain your experience and core design patterns in {skills_list[0] if skills_list else 'software engineering'}.",
            f"How do you approach debugging and performance optimization in {skills_list[-1] if skills_list else 'your stack'}?",
            f"Walk me through the architecture of a complex project you developed with {', '.join(skills_list)}."
        ][:args.questions]

    speaker = AgentSpeaker()

    # 2. Initialize Proctoring ML Engines
    print("[2/5] Initializing Eye & Lip Trackers...")
    gaze_tracker = GazeTracker(away_alert_sec=config.GAZE_AWAY_ALERT_SEC)
    lip_tracker = LipTracker(talking_threshold=config.MAR_TALKING_THRESHOLD)
    presence_tracker = PresenceTracker(missing_alert_sec=config.FACE_MISSING_ALERT_SEC)
    scorer = IntegrityScorer(initial_score=100.0)
    hud = ProctorHUD()

    # 3. Initialize Audio Energy Monitor
    print("[3/5] Starting Background Audio Monitor...")
    audio_monitor = AudioMonitor(speech_threshold=config.AUDIO_SPEECH_THRESHOLD)
    audio_monitor.start()

    # 4. Initialize Face Mesh Engine (compatible with both legacy and modern MediaPipe)
    print("[4/5] Loading Face Mesh Engine (Iris Landmarks 468/473)...")
    from proctor.face_mesh import get_face_mesh
    face_mesh = get_face_mesh(max_num_faces=2)

    # 5. Open Camera Capture
    print(f"[5/5] Connecting to Camera Device {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"Error: Unable to open camera device index {args.camera}. Please check connection.")
        audio_monitor.stop()
        sys.exit(1)

    print("\n>>> INTERVIEW SESSION LAUNCHED. FOCUS ON CAMERA WINDOW. <<<")
    print("Controls: [N] Next Question  |  [Q] Exit & Generate Audit Report\n")

    # State Machine variables
    current_q_idx = 0
    q_start_time = time.time()
    has_spoken_current_q = False
    is_finished = False
    is_evaluating = False
    eval_feedback = ""
    eval_feedback_expire = 0.0
    question_responses = []

    def submit_and_advance():
        nonlocal current_q_idx, q_start_time, has_spoken_current_q, is_finished, is_evaluating, eval_feedback, eval_feedback_expire
        if is_finished or is_evaluating:
            return

        is_evaluating = True
        current_q_text = questions[current_q_idx]
        transcript = audio_monitor.get_transcript()

        print(f"\n[AI Evaluation] Checking candidate's response to Question {current_q_idx + 1}...")
        print(f"  Transcript: \"{transcript if transcript else '[No verbal response recorded]'}\"")

        # Evaluate with Gemini
        eval_res = agent.evaluate_answer(current_q_text, transcript)
        verdict = eval_res.get("verdict", "ACCEPTABLE")
        score = eval_res.get("score", 7)
        feedback = eval_res.get("feedback", "Response reviewed.")

        print(f"  Result: {verdict} ({score}/10) | {feedback}")

        question_responses.append({
            "question": current_q_text,
            "transcript": transcript if transcript else "No verbal response recorded.",
            "evaluation": eval_res
        })

        eval_feedback = f"{verdict} ({score}/10): {feedback}"
        eval_feedback_expire = time.time() + 4.0

        if current_q_idx + 1 < len(questions):
            current_q_idx += 1
            q_start_time = time.time()
            has_spoken_current_q = False
            audio_monitor.clear_transcript()
            speaker.speak_async(f"Response checked. Next question.")
            print(f"[Interview] Advanced to Question {current_q_idx + 1}\n")
        else:
            is_finished = True
            speaker.speak_async("Thank you. All questions have been completed.")
            print("[Interview] All questions completed.\n")

        is_evaluating = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Warning: Camera frame read failed. Retrying...")
                time.sleep(0.05)
                continue

            # Mirror frame horizontally for intuitive webcam view
            frame = cv2.flip(frame, 1)
            frame_h, frame_w = frame.shape[:2]

            # Trigger AI Agent Voice for Current Question
            if not has_spoken_current_q and not is_finished:
                current_q_text = questions[current_q_idx]
                audio_monitor.set_recording_enabled(False)  # Mute STT while AI reads question
                speaker.speak_async(current_q_text)
                has_spoken_current_q = True

            # Enable mic STT once agent finishes reading the question
            if has_spoken_current_q and not speaker.is_speaking() and not audio_monitor.recording_enabled:
                audio_monitor.set_recording_enabled(True)

            # Calculate remaining time for current question
            elapsed_q_time = time.time() - q_start_time
            time_remaining = max(0, int(args.time_per_q - elapsed_q_time))

            # Auto-check and advance question on silence after answer OR when time expires
            candidate_transcript = audio_monitor.get_transcript()
            silence_after_answer = audio_monitor.get_silence_after_speech()
            has_answered = len(candidate_transcript.split()) >= 3

            if has_spoken_current_q and not speaker.is_speaking() and not is_evaluating and not is_finished:
                if (has_answered and silence_after_answer >= 3.0) or (time_remaining <= 0):
                    submit_and_advance()

            # Process Face Mesh
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = face_mesh.process(rgb_frame)
            rgb_frame.flags.writeable = True

            face_count = len(results.multi_face_landmarks) if (results and results.multi_face_landmarks) else 0

            # Proctoring telemetry updates
            if face_count > 0:
                primary_landmarks = results.multi_face_landmarks[0].landmark
                gaze_data = gaze_tracker.update(primary_landmarks, frame_w, frame_h)
                lip_data = lip_tracker.update(primary_landmarks, frame_w, frame_h)
            else:
                gaze_data = {"direction": "UNKNOWN", "is_away": False, "duration": 0.0}
                lip_data = {"mar": 0.0, "is_moving": False, "duration": 0.0}

            presence_data = presence_tracker.update(face_count)
            audio_data = audio_monitor.get_status()

            # Ignore audio speech while AI agent is reading a question aloud
            if speaker.is_speaking():
                audio_data = {
                    "volume": audio_data.get("volume", 0.0),
                    "is_speaking": False,
                    "available": audio_data.get("available", False),
                    "transcript": ""
                }

            # Run Integrity Scoring & Anomaly Evaluation
            score_data = scorer.evaluate(gaze_data, lip_data, audio_data, presence_data)

            # Determine Lip Movement Status Text
            if "FLAG: SILENT LIP MOVEMENT" in " ".join(score_data.get("active_alerts", [])):
                lip_display_status = "WHISPERING!"
            elif lip_data.get("is_moving", False):
                lip_display_status = "TALKING"
            else:
                lip_display_status = "STATIC"

            # Construct Proctor State
            proctor_state = {
                "score": score_data.get("score", 100),
                "status": score_data.get("status", "CLEAN"),
                "gaze_direction": gaze_data.get("direction", "CENTER"),
                "is_gaze_away": gaze_data.get("is_away", False),
                "lip_status": lip_display_status,
                "mar": lip_data.get("mar", 0.0),
                "audio_speaking": audio_data.get("is_speaking", False),
                "audio_volume": audio_data.get("volume", 0.0),
                "face_count": face_count,
                "active_alerts": score_data.get("active_alerts", []),
                "infractions_count": score_data.get("infractions_count", 0)
            }

            # Clear temporary evaluation feedback toast after expiration
            active_feedback = eval_feedback if (time.time() < eval_feedback_expire) else ""

            # Construct Interview State
            interview_state = {
                "question_idx": current_q_idx + 1,
                "total_questions": len(questions),
                "current_question": questions[current_q_idx] if not is_finished else "Interview Complete.",
                "time_remaining": time_remaining if not is_finished else 0,
                "is_finished": is_finished,
                "transcript": candidate_transcript,
                "is_evaluating": is_evaluating,
                "eval_feedback": active_feedback
            }

            # Render High-Tech HUD
            frame = hud.draw_hud(frame, interview_state, proctor_state)

            # Display Output Window
            cv2.imshow("AI Proctored Interview System - HUD", frame)

            # Keyboard Input Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('n') and not is_finished:  # Submit answer & advance
                submit_and_advance()

    finally:
        # Cleanup Resources
        cap.release()
        cv2.destroyAllWindows()
        face_mesh.close()
        audio_monitor.stop()
        speaker.shutdown()

        # Save Final Audit Report
        final_summary = scorer.get_summary()
        report_payload = {
            "skills_tested": skills_list,
            "questions_asked": questions,
            "question_responses": question_responses,
            "final_integrity_score": final_summary["final_score"],
            "integrity_classification": "CLEAN" if final_summary["final_score"] >= 85 else (
                "SUSPICIOUS" if final_summary["final_score"] >= 65 else "HIGH_RISK"
            ),
            "total_infractions_flagged": final_summary["total_infractions"],
            "infractions_timeline": final_summary["infractions_log"]
        }

        report_file = save_report(report_payload)

        print("\n=======================================================")
        print("             INTERVIEW AUDIT SUMMARY                   ")
        print("=======================================================")
        print(f"  Final Integrity Score: {report_payload['final_integrity_score']}%")
        print(f"  Classification:        {report_payload['integrity_classification']}")
        print(f"  Total Infractions:     {report_payload['total_infractions_flagged']}")
        print(f"  Audit Report Saved To: {report_file}")
        print("=======================================================\n")


if __name__ == "__main__":
    main()
