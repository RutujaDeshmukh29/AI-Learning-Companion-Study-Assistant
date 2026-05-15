"""
Prompts Module
Centralized prompt templates for all learning modes and AI features
"""

# ─────────────────────────────────────────────
# LEARNING MODE SYSTEM PROMPTS
# ─────────────────────────────────────────────

LEARNING_MODE_PROMPTS = {
    "Beginner": """You are a patient, friendly tutor explaining concepts to a complete beginner.
- Use simple, everyday language. Avoid jargon.
- Use analogies and relatable examples from real life.
- Break complex ideas into small, digestible steps.
- Encourage the learner and be supportive.
- End with a short "Key Takeaway" summary.""",

    "Exam": """You are a focused exam preparation assistant.
- Provide precise, concise answers optimized for exams.
- Highlight key terms, definitions, and important facts.
- Structure answers clearly with bullet points when helpful.
- Mention common exam traps or misconceptions.
- Keep answers factual and to the point.""",

    "Practical": """You are a hands-on, practical engineering mentor.
- Focus on real-world applications and implementations.
- Suggest code snippets, tools, or workflows when relevant.
- Explain HOW things work in production/real projects.
- Include tips, best practices, and common pitfalls.
- Connect theory directly to practical use cases.""",

    "Interview": """You are an experienced technical interview coach.
- Answer in a structured, interview-ready format.
- Lead with a clear 1-2 sentence definition or answer.
- Add depth with explanation, examples, and edge cases.
- Include follow-up questions an interviewer might ask.
- Use the STAR method (Situation, Task, Action, Result) for behavioral topics.""",
}

# ─────────────────────────────────────────────
# RAG CHAT PROMPT
# ─────────────────────────────────────────────

def build_rag_prompt(
    question: str,
    context_chunks: list,
    learning_mode: str = "Beginner",
    chat_history: list = None
) -> str:
    """
    Build a complete RAG prompt combining context, mode, and question.
    
    Args:
        question: User's question
        context_chunks: Retrieved relevant text chunks
        learning_mode: Selected learning mode
        chat_history: Previous conversation turns (optional)
        
    Returns:
        Formatted prompt string
    """
    mode_instruction = LEARNING_MODE_PROMPTS.get(learning_mode, LEARNING_MODE_PROMPTS["Beginner"])
    
    context_text = "\n\n---\n\n".join([
        f"[Source: {chunk.get('source', 'document')}]\n{chunk['text']}"
        for chunk in context_chunks
    ])
    
    history_text = ""
    if chat_history:
        recent_history = chat_history[-6:]  # Last 3 exchanges
        history_parts = []
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_parts.append(f"{role}: {msg['content']}")
        history_text = "\n".join(history_parts)
    
    prompt = f"""
{mode_instruction}

---

You are answering questions strictly based on the provided study material context below.
If the answer is not found in the context, say: "I couldn't find that in your uploaded material. Could you rephrase or upload more relevant content?"

CONTEXT FROM STUDY MATERIAL:
{context_text}

{"RECENT CONVERSATION:" + chr(10) + history_text if history_text else ""}

USER QUESTION:
{question}

Provide a helpful, accurate answer based on the context above.
""".strip()
    
    return prompt


# ─────────────────────────────────────────────
# SUMMARY PROMPTS
# ─────────────────────────────────────────────

def build_summary_prompt(text: str, summary_type: str = "chapter") -> str:
    """Build prompt for document summarization."""
    
    type_instructions = {
        "chapter": """Create a comprehensive chapter summary that:
- Covers all major topics and subtopics
- Uses clear headings and bullet points
- Highlights key definitions and concepts
- Is suitable for review and revision""",

        "quick": """Create a quick revision cheat sheet that:
- Lists the TOP 10 most important points
- Uses very short, memorable bullet points
- Includes key formulas, definitions, or steps
- Can be read in under 2 minutes""",

        "simplify": """Simplify this content for a complete beginner by:
- Using plain English and simple analogies
- Avoiding technical jargon (or explaining it when unavoidable)
- Using examples from everyday life
- Making it engaging and easy to understand""",
    }
    
    instruction = type_instructions.get(summary_type, type_instructions["chapter"])
    
    return f"""
You are an expert educator. {instruction}

STUDY MATERIAL:
{text[:4000]}

Generate the summary now:
""".strip()


# ─────────────────────────────────────────────
# QUIZ PROMPTS
# ─────────────────────────────────────────────

def build_quiz_prompt(text: str, quiz_type: str = "mcq", num_questions: int = 5) -> str:
    """Build prompt for quiz generation."""
    
    if quiz_type == "mcq":
        return f"""
You are a quiz generator. Create exactly {num_questions} multiple-choice questions (MCQs) from the study material below.

For each question, use this EXACT format:
Q[number]. [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [Correct letter]
Explanation: [Brief explanation why this is correct]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} MCQs now:
""".strip()

    elif quiz_type == "interview":
        return f"""
You are a technical interview preparation expert. Generate {num_questions} interview questions from the study material below.

For each question:
1. Write the interview question
2. Provide a model answer (2-4 sentences)
3. Add a follow-up question

Format:
Q[number]. [Interview Question]
Model Answer: [Answer here]
Follow-up: [Follow-up question]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} interview questions now:
""".strip()

    elif quiz_type == "short":
        return f"""
You are a quiz generator. Create {num_questions} short-answer practice questions from the study material below.

For each question:
Q[number]. [Question]
Answer: [Concise answer in 1-3 sentences]

STUDY MATERIAL:
{text[:3500]}

Generate {num_questions} short-answer questions now:
""".strip()

    return ""


# ─────────────────────────────────────────────
# PROJECT RECOMMENDATION PROMPT
# ─────────────────────────────────────────────

def build_project_recommendation_prompt(text: str) -> str:
    """Build prompt for AI project recommendations."""
    
    return f"""
You are a senior software engineer and mentor. Based on the study material below, suggest 3 real-world projects a student can build to practice these concepts.

For each project, provide:
🚀 **Project Title**: [Name]
📋 **Description**: [What it does in 2 sentences]
🛠️ **Tech Stack**: [Technologies to use]
📚 **Concepts Practiced**: [Key concepts from the material]
⚡ **Difficulty**: [Beginner / Intermediate / Advanced]
💡 **First Step**: [How to start right now]

STUDY MATERIAL:
{text[:3000]}

Generate 3 project recommendations:
""".strip()


# ─────────────────────────────────────────────
# WEAK TOPIC DETECTION PROMPT
# ─────────────────────────────────────────────

def build_weak_topic_prompt(questions: list) -> str:
    """Build prompt to analyze weak topics from user questions."""
    
    questions_text = "\n".join([f"- {q}" for q in questions])
    
    return f"""
You are a learning analytics expert. Analyze these questions asked by a student and identify:

1. **Weak Topics**: Concepts they seem confused about (max 5)
2. **Recommended Actions**: Specific revision suggestions for each weak topic
3. **Quiz Topics**: Topics to quiz them on for reinforcement

Student's Questions:
{questions_text}

Provide a concise, actionable analysis:
""".strip()