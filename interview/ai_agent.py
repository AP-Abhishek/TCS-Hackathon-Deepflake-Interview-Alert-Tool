"""
interview/ai_agent.py
---------------------
Responsible: Person 3 (AI Interviewer - Gemini Integration)

TASK OBJECTIVE:
- Connect to Google Gemini API using GEMINI_API_KEY from config.py.
- Accept a list of technical skills (e.g. ["Python", "Machine Learning", "SQL"]) and question count.
- Generate realistic, technical interview questions tailored to the candidate's skills.
- Return the questions as a structured list of strings.

TODO for Person 3:
1. Initialize Gemini client (e.g. using `google-genai` or `google-generativeai`).
2. Construct a prompt instructing Gemini to return exact N interview questions for the given skills.
3. Parse the LLM response into a clean Python list: List[str].
4. Add a fallback list of default questions in case of API failure or offline mode.
"""

from typing import List
import config


class AIInterviewAgent:
    def __init__(self, api_key: str = None):
        """
        TODO:
        - Store API key (use config.GEMINI_API_KEY if not provided).
        - Configure Gemini client/model.
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        # TODO: Initialize Gemini generative model here

    def generate_questions(self, skills: List[str], num_questions: int = 3) -> List[str]:
        """
        TODO:
        - Formulate system prompt: "You are a senior technical interviewer..."
        - Ask Gemini to generate `num_questions` tailored to `skills`.
        - Return a list of strings: ["Question 1...", "Question 2...", ...]
        """
        # Placeholder / Fallback questions until Gemini call is wired up:
        skills_str = ", ".join(skills)
        return [
            f"Can you explain the core concepts and best practices in {skills_str}?",
            f"How do you handle performance bottlenecks or debugging in {skills[0] if skills else 'your stack'}?",
            f"Describe an end-to-end project where you applied {skills_str}."
        ]
