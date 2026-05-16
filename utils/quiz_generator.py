"""
Quiz Generator Module
Generates MCQs, interview questions, and practice quizzes using Gemini
"""

from typing import List, Dict, Any
from utils.llm import ask_llm
from utils.prompts import build_quiz_prompt
import re


def generate_mcqs(text: str, num_questions: int = 5) -> str:
    """
    Generate multiple choice questions from study material.
    
    Args:
        text: Study material text
        num_questions: Number of MCQs to generate
        
    Returns:
        Formatted MCQ string
    """
    prompt = build_quiz_prompt(text, quiz_type="mcq", num_questions=num_questions)
    response = ask_llm(prompt)
    return response


def generate_interview_questions(text: str, num_questions: int = 5) -> str:
    """
    Generate interview-style questions with model answers.
    
    Args:
        text: Study material text
        num_questions: Number of questions to generate
        
    Returns:
        Formatted interview questions string
    """
    prompt = build_quiz_prompt(text, quiz_type="interview", num_questions=num_questions)
    response = ask_llm(prompt)
    return response


def generate_short_answer_questions(text: str, num_questions: int = 5) -> str:
    """
    Generate short answer practice questions.
    
    Args:
        text: Study material text
        num_questions: Number of questions to generate
        
    Returns:
        Formatted short answer questions string
    """
    prompt = build_quiz_prompt(text, quiz_type="short", num_questions=num_questions)
    response = ask_llm(prompt)
    return response


def parse_mcqs(mcq_text: str) -> List[Dict[str, Any]]:
    """
    Parse MCQ text into structured question objects.
    
    Args:
        mcq_text: Raw MCQ text from Gemini
        
    Returns:
        List of structured MCQ dicts
    """
    questions = []
    
    # Split by question pattern
    question_blocks = re.split(r'Q\d+\.', mcq_text)
    
    for block in question_blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        if not lines:
            continue
        
        question = {
            "question": lines[0].strip(),
            "options": {},
            "answer": "",
            "explanation": ""
        }
        
        for line in lines[1:]:
            line = line.strip()
            if re.match(r'^[A-D]\)', line):
                key = line[0]
                question["options"][key] = line[3:].strip()
            elif line.startswith("Answer:"):
                question["answer"] = line.replace("Answer:", "").strip()
            elif line.startswith("Explanation:"):
                question["explanation"] = line.replace("Explanation:", "").strip()
        
        if question["question"] and question["options"]:
            questions.append(question)
    
    return questions


def format_quiz_for_display(quiz_text: str, quiz_type: str = "mcq") -> str:
    """
    Add markdown formatting to quiz output for better display.
    
    Args:
        quiz_text: Raw quiz text from Gemini
        quiz_type: Type of quiz ('mcq', 'interview', 'short')
        
    Returns:
        Formatted quiz text with markdown
    """
    if not quiz_text:
        return "No quiz generated."
    
    # Add separator between questions for readability
    formatted = re.sub(r'(Q\d+\.)', r'\n---\n**\1**', quiz_text)
    
    # Bold answer lines
    formatted = re.sub(r'(Answer:)', r'✅ **\1**', formatted)
    formatted = re.sub(r'(Explanation:)', r'💡 **\1**', formatted)
    formatted = re.sub(r'(Model Answer:)', r'📝 **\1**', formatted)
    formatted = re.sub(r'(Follow-up:)', r'🔄 **\1**', formatted)
    
    return formatted.strip()