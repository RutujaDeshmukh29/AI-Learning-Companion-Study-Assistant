"""
Quiz Generator Module
======================
Changes from original:
- Was importing from utils.llm (ask_llm) correctly -- kept that.
- Was importing build_quiz_prompt from utils.prompts -- but that function
  didn't exist in the original prompts.py. Now it does (added in our new prompts.py).
- Added format_quiz_for_display() for markdown-enhanced rendering in the UI.
- Added generate_project_recommendations() and generate_weak_topic_analysis()
  so the UI can call a single module for all AI generation tasks.
"""

import re
from typing import List, Dict, Any

from utils.llm import ask_llm
from utils.prompts import (
    build_quiz_prompt,
    build_project_recommendation_prompt,
    build_weak_topic_prompt,
    build_summary_prompt,
)


# ────────────────────────────────────────────────────────────────────────────
# QUIZ GENERATORS
# ────────────────────────────────────────────────────────────────────────────
def generate_mcqs(text: str, num_questions: int = 5) -> str:
    """Generate multiple choice questions from study material."""
    prompt = build_quiz_prompt(text, quiz_type="mcq", num_questions=num_questions)
    return ask_llm(prompt)


def generate_interview_questions(text: str, num_questions: int = 5) -> str:
    """Generate interview-style questions with model answers."""
    prompt = build_quiz_prompt(text, quiz_type="interview", num_questions=num_questions)
    return ask_llm(prompt)


def generate_short_answer_questions(text: str, num_questions: int = 5) -> str:
    """Generate short-answer practice questions."""
    prompt = build_quiz_prompt(text, quiz_type="short", num_questions=num_questions)
    return ask_llm(prompt)


# ────────────────────────────────────────────────────────────────────────────
# SUMMARY GENERATORS
# ────────────────────────────────────────────────────────────────────────────
def generate_summary(text: str, summary_type: str = "chapter") -> str:
    """
    Generate document summary.
    summary_type: "chapter" | "quick" | "simplify"
    """
    prompt = build_summary_prompt(text, summary_type=summary_type)
    return ask_llm(prompt)


# ────────────────────────────────────────────────────────────────────────────
# PROJECT RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────────
def generate_project_recommendations(text: str) -> str:
    """Generate real-world project ideas based on study material topics."""
    prompt = build_project_recommendation_prompt(text)
    return ask_llm(prompt)


# ────────────────────────────────────────────────────────────────────────────
# WEAK TOPIC ANALYSIS
# ────────────────────────────────────────────────────────────────────────────
def generate_weak_topic_analysis(questions: List[str]) -> str:
    """Analyse the user's question history to identify weak areas."""
    prompt = build_weak_topic_prompt(questions)
    return ask_llm(prompt)


# ────────────────────────────────────────────────────────────────────────────
# DISPLAY FORMATTER
# ────────────────────────────────────────────────────────────────────────────
def format_quiz_for_display(quiz_text: str, quiz_type: str = "mcq") -> str:
    """
    Add markdown formatting to raw LLM quiz output for cleaner UI rendering.
    Works on all quiz types.
    """
    if not quiz_text:
        return "No quiz generated."

    # Insert horizontal rules + bold question numbers
    formatted = re.sub(r'(Q\d+\.)', r'\n---\n**\1**', quiz_text)

    # Highlight special lines with icons
    formatted = re.sub(r'\b(Answer:)',       r'✅ **\1**',  formatted)
    formatted = re.sub(r'\b(Explanation:)',  r'💡 **\1**',  formatted)
    formatted = re.sub(r'\b(Model Answer:)', r'📝 **\1**',  formatted)
    formatted = re.sub(r'\b(Follow-up:)',    r'🔄 **\1**',  formatted)

    return formatted.strip()


# ────────────────────────────────────────────────────────────────────────────
# MCQ PARSER (structured output)
# ────────────────────────────────────────────────────────────────────────────
def parse_mcqs(mcq_text: str) -> List[Dict[str, Any]]:
    """
    Parse raw MCQ text into structured dicts.
    Useful if you want to build an interactive quiz UI later.

    Returns:
        [{"question": "...", "options": {"A": "...", ...},
          "answer": "B", "explanation": "..."}, ...]
    """
    questions = []
    for block in re.split(r'Q\d+\.', mcq_text):
        block = block.strip()
        if not block:
            continue
        lines    = block.split('\n')
        q        = {"question": lines[0].strip(), "options": {}, "answer": "", "explanation": ""}
        for line in lines[1:]:
            line = line.strip()
            if re.match(r'^[A-D]\)', line):
                q["options"][line[0]] = line[3:].strip()
            elif line.startswith("Answer:"):
                q["answer"] = line.replace("Answer:", "").strip()
            elif line.startswith("Explanation:"):
                q["explanation"] = line.replace("Explanation:", "").strip()
        if q["question"] and q["options"]:
            questions.append(q)
    return questions
