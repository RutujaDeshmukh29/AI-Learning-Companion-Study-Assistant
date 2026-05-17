# 🧠 AI Learning Companion

> A production-grade, full-featured AI-powered study platform — built as a portfolio-quality AI engineering project.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What It Does

Upload any PDF (lecture notes, textbooks, research papers) and unlock:

### Core Features

| Feature | Use | Uniqueness |
| :--- | :--- | :--- |
| 📚 **Multi-PDF Upload** | Upload and process multiple PDF documents at once. | The app handles each file individually, showing separate progress and status, and sets the last one as the active document. |
| 💬 **RAG Chat** | Ask questions about your uploaded documents and get answers. | It uses a **Hybrid RAG** model, which means it can answer based on your document but also expand with its general knowledge for richer, more complete answers. |
| 🗺️ **Roadmap Generator** | Get a personalized, step-by-step learning plan for any goal. | Tracks your progress with checkboxes and a completion percentage, and this progress is saved even if you log out. |
| 🔀 **Diagram Generation** | Create flowcharts, mind maps, and other diagrams from a text description. | It uses a client-side rendering library (Mermaid.js), which means there is no extra cost for using an external API, and it works offline. |
| 📋 **Smart Summaries** | Get different types of summaries from your documents. | You can choose between a detailed chapter summary, a quick "cheat sheet", or a simplified explanation for complex topics. |
| ❓ **Quiz Engine** | Test your knowledge with various types of questions. | It's not just MCQs. It can generate interview questions, short-answer questions, and even coding challenges based on the content of your PDFs. |
| 📊 **Analytics Dashboard** | See your learning progress and habits at a glance. | It tracks your study streak, shows you which topics you've studied the most, and visualizes how you use the different learning modes. |
| 📁 **Session History** | Revisit any of your past chat sessions. | Your conversations are saved per user, so you can always go back to a previous session to review answers or continue a conversation. |
| 🔊 **Voice Assistant** | Use your voice to ask questions and hear the AI's answers. | This feature is built using your browser's native speech capabilities, which means it's free to use and doesn't rely on paid external services. |
| 🎓 **6 Learning Modes** | Tailor the AI's personality and response style to your needs. | You can switch between modes like "Beginner" for simple explanations, "Exam" for revision, or "Practical" for coding help. |
| 🔐 **Authentication** | Securely sign up and log in to the application. | Each user has their own account, and all uploaded documents and chat histories are kept private and isolated. |
| 🏆 **Coding Challenges** | Generates coding problems based on study material or a specified topic. | Helps reinforce learning with practical application, tailored difficulty and language. |
| 🚀 **Project Recommendations** | Suggests relevant project ideas based on the content of your documents. | Connects theoretical knowledge to real-world application, fostering deeper understanding. |
| 🎯 **Weak Topic Analysis** | Identifies areas where you might need more study based on your chat questions. | Provides personalized feedback to focus your learning efforts efficiently. |

### Key Technical Uniqueness

*   **Fast & Efficient:** The app is engineered to be fast. It processes and indexes your documents once, so asking questions is quick. It also uses smart chunking to improve the quality of the answers.
*   **Flexible & Adaptable:** The application is not tied to a single AI provider. You can easily switch between different LLMs like Groq, Gemini, or OpenAI by changing a single setting.
*   **Cost-Effective:** By using browser-native APIs for voice and client-side rendering for diagrams, the application keeps costs down and avoids reliance on paid external services.
*   **Robust & Scalable:** The use of SQLite for the database and content-aware chunking for documents makes the application robust and ready to be scaled up.

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │         app.py (Streamlit UI)    │
                    │  8 tabs · Auth guard · Session   │
                    └────────────┬────────────────────┘
                                 │
           ┌─────────────────────┼──────────────────────┐
           │                     │                      │
    ┌──────▼──────┐    ┌────────▼────────┐    ┌────────▼────────┐
    │  RAG Layer  │    │  Feature Layer  │    │   Auth Layer    │
    │             │    │                 │    │                 │
    │ pdf_loader  │    │ roadmap.py      │    │ auth_manager.py │
    │ splitter    │    │ diagram.py      │    │ auth_ui.py      │
    │ embeddings  │    │ analytics.py    │    │ SQLite users.db │
    │ vector_store│    │ history.py      │    └─────────────────┘
    │ rag_pipeline│    │ voice.py        │
    └──────┬──────┘    │ quiz_generator  │
           │           └────────┬────────┘
    ┌──────▼──────┐            │
    │  ChromaDB   │    ┌────────▼────────┐
    │  (vectors)  │    │    LLM Layer    │
    └─────────────┘    │    llm.py       │
                       │ Groq/OpenAI/    │
                       │ Gemini          │
                       └─────────────────┘
```

### Key Engineering Decisions

| Decision | Why |
|----------|-----|
| **Indexing ≠ Querying** | Embeddings generated once on upload, not per question — 10x faster chat |
| **Content-hash chunk IDs** | Multi-PDF support without ID collisions, idempotent re-uploads |
| **Provider-agnostic LLM layer** | Swap Groq → Gemini → OpenAI via one `.env` line |
| **Browser Web Speech API** | Free voice I/O — no paid TTS/STT API needed |
| **Mermaid.js diagrams** | Text-based diagrams render client-side — zero cost, fully offline-capable |
| **SQLite for auth + history** | Zero-dependency persistence, easy Postgres upgrade path |
| **Sentence-aware chunking** | No mid-sentence cuts → higher retrieval quality |
| **Hybrid RAG mode** | Doc-grounded answer + AI expansion gives richer responses |

---

## 📁 Project Structure

```
ai-learning-companion/
├── app.py                      # Main Streamlit app (8 tabs)
├── requirements.txt
├── .env.example
│
├── auth/
│   ├── auth_manager.py         # SQLite auth: signup/login/logout/sessions
│   └── auth_ui.py              # Login & signup UI
│
├── utils/
│   ├── llm.py                  # Provider-agnostic LLM (Groq/OpenAI/Gemini)
│   ├── pdf_loader.py           # PyMuPDF text extraction
│   ├── text_splitter.py        # Sentence-aware overlapping chunks
│   ├── embeddings.py           # sentence-transformers embeddings
│   ├── vector_store.py         # ChromaDB: store, retrieve, multi-doc
│   ├── rag_pipeline.py         # index_document() + query_rag() (separated)
│   ├── prompts.py              # All prompts + 6 learning mode system
│   ├── quiz_generator.py       # MCQ, interview, summary, project generation
│   ├── roadmap.py              # Roadmap generation + progress tracking
│   ├── diagram.py              # Mermaid diagram generation + rendering
│   ├── history.py              # Persistent chat history + saved outputs
│   ├── analytics.py            # Study streaks, topic trends, activity
│   └── voice.py                # Browser Web Speech API (STT + TTS)
│
├── data/
│   ├── uploaded_pdfs/          # Per-user PDF storage (gitignored)
│   └── users.db                # SQLite: users, sessions, history (gitignored)
│
└── tests/
    └── tests/
        ├── test_pdf.py
        ├── test_splitter.py
        ├── test_embeddings.py
        ├── test_vector_store.py
        ├── test_rag.py
        └── test_llm.py
```
---

For screenshots and a demo video, please check the [assets folder](./assets).

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/RutujaDeshmukh29/AI-Learning-Companion-Study-Assistant.git
cd ai-learning-companion

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env: set LLM_PROVIDER and your API key

# 5. Run
streamlit run app.py
```

---

## 🔑 API Keys (Free Tier Available)

| Provider | Speed | Cost | Get Key |
|----------|-------|------|---------|
| **Groq** ⭐ | Very fast | Free | [console.groq.com](https://console.groq.com) |
| **Gemini** | Fast | Free (1M tokens/month) | [aistudio.google.com](https://aistudio.google.com) |
| **OpenAI** | Standard | Paid | [platform.openai.com](https://platform.openai.com) |

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**
3. Select repo, set main file: `app.py`
4. **Advanced → Secrets**:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "your_key_here"
   ```
5. Click **Deploy**

---

## 🎓 Learning Modes Explained

| Mode | Best For | AI Behaviour |
|------|----------|-------------|
| 🌱 **Beginner** | First-time learners | Simple language, analogies, numbered steps |
| 📝 **Exam** | Pre-exam revision | Concise, bullet-pointed, exam-focused |
| ⚙️ **Practical** | Developers | Code snippets, tools, production patterns |
| 💼 **Interview** | Job prep | STAR format, follow-up questions |
| 🔬 **Research** | Deep study | Academic analysis, open questions |
| 🗺️ **Roadmap** | Planning | Phase-by-phase learning paths |

---

## 🗺️ Roadmap Generation

The standout feature. Tell the AI your goal:
> *"I want to become a machine learning engineer"*

The AI generates:
- Phase-by-phase learning path (Foundation → Core → Advanced → Projects)
- Specific topics per phase with explanations
- Estimated time per phase
- Concrete project ideas
- Week 1 action plan

Progress is tracked with checkboxes and a completion percentage, persisted to SQLite so it survives page refreshes and re-logins.

---

## 🔀 Diagram Generation

Uses Mermaid.js (client-side rendering — no API cost):
- **Flowchart** — process flows, algorithms, decision trees
- **Mind Map** — concept hierarchies, topic relationships
- **Sequence** — API interactions, system communications
- **Class Diagram** — OOP structures, data models

---

## 🔊 Voice Assistant

Uses browser-native Web Speech API (Chrome/Edge):
- **Voice Input** — click mic, speak your question, transcript auto-fills
- **Voice Output** — AI responses read aloud via SpeechSynthesis
- **Zero cost** — no external TTS/STT API required
- Requires HTTPS (Streamlit Cloud uses HTTPS ✅)

---

## 🔮 Future Roadmap

- [ ] OCR support for scanned PDFs (Tesseract)
- [ ] Multi-language support (Google Translate API)
- [ ] Anki flashcard export
- [ ] Study reminders (email/push notifications)
- [ ] Cloud storage (Supabase/S3 for PDFs)
- [ ] Real-time collaboration (shared study sessions)
- [ ] AI-generated concept dependency graphs
- [ ] Mobile app (Streamlit + PWA)

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Web interface |
| LLM | Groq (Llama 3.1) | AI responses |
| Embeddings | sentence-transformers | Semantic search |
| Vector DB | ChromaDB | Document retrieval |
| PDF | PyMuPDF | Text extraction |
| Diagrams | Mermaid.js | Visual generation |
| Voice | Web Speech API | STT + TTS |
| Auth | SQLite + bcrypt | User accounts |
| Deployment | Streamlit Cloud | Free hosting |

---

### 🔗 Live Demo & Contact

Experience the AI Learning Companion live: **[https://ai-learning-companion-study-assistanti.streamlit.app/](https://ai-learning-companion-study-assistanti.streamlit.app/)**

For inquiries, please contact: **deshmukhrutuja2908@gmail.com**

---

*Built as a portfolio-quality AI engineering project. Demonstrates: RAG architecture, vector search, multi-modal AI, production auth, analytics, and modern UI/UX.*

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by Rutuja Deshmukh

</div>
