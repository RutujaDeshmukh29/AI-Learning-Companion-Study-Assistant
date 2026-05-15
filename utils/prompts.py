def build_rag_prompt(context, question):
    """
    Build prompt using retrieved context.
    """

    prompt = f"""
You are an AI Learning Companion.

Answer the user's question using ONLY the provided context.

If the answer is not available in the context, say:
"I could not find the answer in the uploaded notes."

---------------------
Context:
{context}
---------------------

Question:
{question}

Answer:
"""

    return prompt