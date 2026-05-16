from utils.gemini_api import ask_gemini

question = "What is Retrieval-Augmented Generation (RAG)?"

response = ask_gemini(question)

print("Gemini Response:")
print(response)
