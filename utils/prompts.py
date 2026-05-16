"""
Prompts Module
===============
WHY this matters architecturally:

All prompt logic lives in ONE place. When you want to tune how the AI
behaves -- make Beginner mode simpler, add a new learning mode, change
citation format -- you edit this file only. Nothing else changes.

This is called the "prompt layer" in production AI systems. Keeping it
separate from LLM code and business logic is critical for maintainability.

Original prompts.py had just one function with no mode support.
This version adds: 4 learning modes, RAG, summary, quiz, project,
weak-topic analysis, and a username-aware greeting.
"""

from typing import List, Dict, Optional


# ────────────────────────────────────────────────────────────────────────────
# LEARNING MODE SYSTEM PROMPTS
# ────────────────────────────────────────────────────────────────────────────
LEARNING_MODES: Dict[str, str] = {
    "Beginner": (
        "You are a patient, encouraging tutor explaining to a complete beginner.\n"
        "- Use plain everyday language. Define every technical term you use.\n"
        "- Use real-life analogies and relatable examples.\n"
        "- Break complex ideas into small numbered steps.\n"
        "- End your answer with a short '💡 Key Takeaway' line."
    ),
    "Exam": (
        "You are a focused exam-prep assistant.\n"
        "- Give precise, concise answers optimised for written exams.\n"
        "- Lead with the definition or direct answer, then add key details.\n"
        "- Bullet-point important facts, formulas, or named concepts.\n"
        "- Flag common exam mistakes with '⚠️ Watch out:'."
    ),
    "Practical": (
        "You are a hands-on engineering mentor.\n"
        "- Focus on real-world application and implementation.\n"
        "- Include code snippets, commands, or tool names where relevant.\n"
        "- Explain HOW to actually use this in a project, not just what it is.\n"
        "- Highlight best practices and common production pitfalls."
    ),
    "Interview": (
        "You are a senior technical interview coach.\n"
        "- Open with a crisp 1-2 sentence textbook-style answer.\n"
        "- Expand with deeper explanation and a concrete example.\n"
        "- Add a '🎤 Follow-up an interviewer might ask:' section.\n"
        "- Use STAR format (Situation / Task / Action / Result) for behavioural topics."
    ),
}

VALID_MODES = list(LEARNING_MODES.keys())
DEFAULT_MODE = "Beginner"


# ────────────────────────────────────────────────────────────────────────────
# RAG CHAT PROMPT  (main prompt used on every user question)
# ────────────────────────────────────────────────────────────────────────────
def build_rag_prompt(
    context: str,
    question: str,
    learning_mode: str = DEFAULT_MODE,
    chat_history: Optional[List[Dict]] = None,
    username: str = None,
) -> str:
    """
    Build the complete RAG prompt combining:
      - Mode-specific teaching style
      - Retrieved context chunks
      - Optional recent conversation history
      - The user's question

    This is the function called on every chat message.
    Original signature build_rag_prompt(context, question) still works.

    Args:
        context:       Concatenated retrieved chunks (plain text).
        question:      User's question.
        learning_mode: One of Beginner / Exam / Practical / Interview.
        chat_history:  Last few turns as [{"role": "user"|"assistant", "content": "..."}].
        username:      Optional first name for a personalised touch.

    Returns:
        Complete prompt string ready to send to the LLM.
    """
    mode_instruction = LEARNING_MODES.get(learning_mode, LEARNING_MODES[DEFAULT_MODE])

    # Recent conversation (last 3 exchanges = 6 messages)
    history_block = ""
    if chat_history:
        recent = chat_history[-6:]
        lines  = []
        for msg in recent:
            role  = "Student" if msg["role"] == "user" else "Tutor"
            lines.append(f"{role}: {msg['content'][:300]}")   # cap length
        history_block = "\n\nRECENT CONVERSATION:\n" + "\n".join(lines)

    user_label = f"Student ({username})" if username else "Student"

    prompt = f"""{mode_instruction}

You are an AI Learning Companion. Answer using ONLY the context below.
If the answer is not in the context, say exactly:
"I couldn't find that in your uploaded material. Try rephrasing or upload more relevant content."
{history_block}

---------------------
CONTEXT FROM STUDY MATERIAL:
{context}
---------------------

{user_label}: {question}

Tutor:"""
    return prompt.strip()


# ────────────────────────────────────────────────────────────────────────────
# SUMMARY PROMPTS
# ────────────────────────────────────────────────────────────────────────────
_SUMMARY_INSTRUCTIONS = {
    "chapter": (
        "Create a comprehensive chapter summary that:\n"
        "- Covers all major topics with clear headings (##)\n"
        "- Uses concise bullet points under each heading\n"
        "- Highlights key definitions in **bold**\n"
        "- Is suitable for revision the night before an exam"
    ),
    "quick": (
        "Create a quick-revision cheat sheet that:\n"
        "- Lists the TOP 10 most important points as short bullets\n"
        "- Includes key formulas, definitions, or steps\n"
        "- Can be read cover-to-cover in under 2 minutes\n"
        "- Uses emojis sparingly to aid memory (✅ ⚠️ 💡)"
    ),
    "simplify": (
        "Re-explain this content for a complete beginner:\n"
        "- Use plain English — no jargon unless you define it first\n"
        "- Use a real-life analogy for every main concept\n"
        "- Keep sentences short and conversational\n"
        "- End with 'What you should remember:' and 3 bullet points"
    ),
}


def build_summary_prompt(text: str, summary_type: str = "chapter") -> str:
    """Build prompt for document summarisation."""
    instruction = _SUMMARY_INSTRUCTIONS.get(summary_type, _SUMMARY_INSTRUCTIONS["chapter"])
    return f"""You are an expert educator. {instruction}

STUDY MATERIAL:
{text[:4500]}

Generate the summary now:""".strip()


# ────────────────────────────────────────────────────────────────────────────
# QUIZ PROMPTS
# ────────────────────────────────────────────────────────────────────────────
def build_quiz_prompt(text: str, quiz_type: str = "mcq", num_questions: int = 5) -> str:
    """
    Build quiz generation prompt.
    quiz_type: "mcq" | "interview" | "short"
    """
    if quiz_type == "mcq":
        return f"""You are a quiz generator. Create exactly {num_questions} MCQs from the study material below.

Use this EXACT format for every question:
Q[N]. [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Answer: [Letter]
Explanation: [One sentence why]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} MCQs now:""".strip()

    if quiz_type == "interview":
        return f"""You are a technical interview coach. Generate {num_questions} interview questions from the material.

Format EXACTLY:
Q[N]. [Interview question]
Model Answer: [2-3 sentence model answer]
Follow-up: [One follow-up question]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} interview questions now:""".strip()

    # short answer
    return f"""You are a quiz generator. Create {num_questions} short-answer practice questions.

Format EXACTLY:
Q[N]. [Question]
Answer: [1-3 sentence answer]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} short-answer questions now:""".strip()


# ────────────────────────────────────────────────────────────────────────────
# PROJECT RECOMMENDATION PROMPT
# ────────────────────────────────────────────────────────────────────────────
def build_project_recommendation_prompt(text: str) -> str:
    """Prompt to generate portfolio-worthy project ideas from study material."""
    return f"""You are a senior software engineer and mentor.
Based on the study material below, suggest 3 real-world projects a student can build to practise these concepts.

For each project use this format:
🚀 **Project Title**: [Name]
📋 **Description**: [What it does — 2 sentences]
🛠️ **Tech Stack**: [Specific technologies]
📚 **Concepts Practised**: [From the material]
⚡ **Difficulty**: Beginner | Intermediate | Advanced
💡 **First Step**: [Concrete action to start today]

STUDY MATERIAL:
{text[:3000]}

Generate 3 project recommendations:""".strip()


# ────────────────────────────────────────────────────────────────────────────
# WEAK TOPIC DETECTION PROMPT
# ────────────────────────────────────────────────────────────────────────────
def build_weak_topic_prompt(questions: List[str]) -> str:
    """Analyse the user's question history to surface weak areas."""
    q_list = "\n".join(f"- {q}" for q in questions)
    return f"""You are a learning analytics expert.
Analyse these questions a student asked and identify their weak areas.

Provide:
1. **Weak Topics** (max 5) — concepts they seem confused about
2. **Why** — brief explanation of the confusion pattern you see
3. **Recommended Actions** — specific revision steps for each weak topic
4. **Suggested Quiz Topics** — 3 topics to quiz them on for reinforcement

Student's questions:
{q_list}

Provide a concise, actionable analysis:""".strip()
