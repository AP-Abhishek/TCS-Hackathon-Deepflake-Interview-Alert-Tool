# 5-Person Team Collaboration & Zero-Merge-Conflict Guide

To avoid merge conflicts during the hackathon, the project is structured with **strict module ownership**. Each person owns a specific set of files and follows a predefined input/output data contract.

---

## 1. Role Distribution & File Ownership

| Team Member | Module & Files | Core Responsibilities | Branch Name |
| :--- | :--- | :--- | :--- |
| **Person 1** | `proctor/gaze.py`<br>`proctor/presence.py` | • Iris tracking (landmarks 468, 473)<br>• Off-screen gaze ratio calculation<br>• Candidate presence & multi-face count | `feat/gaze-presence` |
| **Person 2** | `proctor/lips.py`<br>`proctor/audio.py` | • Mouth Aspect Ratio (MAR)<br>• Candidate speaking vs closed lips<br>• Background mic energy level sampling | `feat/lips-audio` |
| **Person 3** | `interview/ai_agent.py`<br>`interview/speaker.py` | • Gemini API call with skills list<br>• Question list generation<br>• Background thread TTS voice output (`pyttsx3`) | `feat/gemini-tts` |
| **Person 4** | `proctor/scoring.py`<br>`reports/generator.py` | • Integrity scoring logic (100% $\rightarrow$ 0%)<br>• Anomaly detection (whispering, external prompter)<br>• Saving JSON & Markdown audit reports | `feat/scoring-reports` |
| **Person 5** | `ui/hud.py`<br>`main.py` | • OpenCV high-tech HUD overlay<br>• Camera loop & key bindings ('q' to quit, 'n' for next)<br>• Integrating everyone's modules | `feat/hud-main` |

---

## 2. Shared Data Contracts (Interfaces)

Each person's function outputs standard Python dictionaries so other modules can consume them without touching your code:

### Person 1 (`proctor/gaze.py` & `presence.py`)
```python
gaze_data = {
    "direction": "CENTER" | "LOOKING_LEFT" | "LOOKING_RIGHT",
    "is_away": bool,
    "duration": float
}

presence_data = {
    "face_count": int,
    "is_missing": bool,
    "is_multiple": bool
}
```

### Person 2 (`proctor/lips.py` & `audio.py`)
```python
lip_data = {
    "mar": float,
    "is_moving": bool,
    "duration": float
}

audio_data = {
    "volume": float,
    "is_speaking": bool
}
```

### Person 3 (`interview/ai_agent.py` & `speaker.py`)
```python
questions = agent.generate_questions(skills=["Python", "ML"], num_questions=3)
# Returns: ["Question 1...", "Question 2...", "Question 3..."]

speaker.speak_async("Here is your first question...")
# Non-blocking background thread
```

### Person 4 (`proctor/scoring.py` & `reports/generator.py`)
```python
score_data = scorer.evaluate(gaze_data, lip_data, audio_data, presence_data)
# Returns:
# {
#   "score": 92,
#   "status": "CLEAN" | "SUSPICIOUS" | "HIGH_RISK",
#   "active_alerts": ["FLAG: LOOKING OFF-SCREEN"]
# }
```

### Person 5 (`ui/hud.py`)
```python
frame = hud.draw_hud(frame, interview_state, proctor_state)
```

---

## 3. Git Workflow Rules (How to Avoid Conflicts)

1. **Rule 1: Never commit directly to `main`**:
   - Everyone creates their assigned branch:
     ```bash
     git checkout -b feat/your-feature
     ```
2. **Rule 2: Edit ONLY your assigned files**:
   - Do NOT modify another team member's file. If you need something from their module, call their function using the predefined dictionary contract above.
3. **Rule 3: Keep `.env` strictly local**:
   - `.env` is already in `.gitignore`. Never force add `.env` to Git. Use `.env.example` as reference.
4. **Rule 4: Pull before merge**:
   - Before merging your branch into `main`:
     ```bash
     git checkout main
     git pull origin main
     git checkout feat/your-feature
     git merge main
     # Verify tests, then merge feat into main
     ```
