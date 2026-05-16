# 🧠 AI Learning Companion

> A production-grade AI-powered study assistant built with Streamlit, ChromaDB, and Groq/Gemini.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What It Does

Upload any PDF (lecture notes, textbooks, research papers) and:
- **Chat** with your documents using RAG (Retrieval-Augmented Generation)
- **Summarise** content in three formats: chapter summary, cheat sheet, simplified
- **Generate quizzes**: MCQs, interview questions, short-answer practice
- **Get project ideas** based on your study material topics
- **Detect weak topics** from your question history

All responses adapt to your chosen **learning mode**: Beginner / Exam / Practical / Interview.

---

## 🏗️ Architecture

```
User Question
     ↓
Embed with sentence-transformers (all-MiniLM-L6-v2)
     ↓
Retrieve top-5 chunks from ChromaDB (cosine similarity)
     ↓
Inject context + mode-specific prompt → LLM (Groq/Gemini/OpenAI)
     ↓
Grounded answer with source citations
```

### Key Design Decisions

| Decision | Why |
|----------|-----|
| **Indexing separated from querying** | Embeddings are generated once on upload, not on every question |
| **Content-hash chunk IDs** | Multiple PDFs coexist safely; re-uploading is idempotent |
| **Provider-agnostic LLM layer** | Swap Groq → OpenAI → Gemini via one `.env` variable |
| **SQLite auth** | Zero extra services, portable, easy to upgrade to Postgres |
| **Sentence-aware chunking** | Chunks never break mid-sentence, improving retrieval quality |

---

## 📁 Project Structure

```
ai-learning-companion/
├── app.py                    # Main Streamlit application
├── requirements.txt
├── .env.example              # Copy to .env and fill in API keys
│
├── auth/
│   ├── auth_manager.py       # SQLite auth: signup / login / logout
│   └── auth_ui.py            # Login & signup UI components
│
├── utils/
│   ├── llm.py                # Provider-agnostic LLM wrapper (Groq/OpenAI/Gemini)
│   ├── pdf_loader.py         # PDF text extraction via PyMuPDF
│   ├── text_splitter.py      # Sentence-aware chunking with overlap
│   ├── embeddings.py         # sentence-transformers embedding generation
│   ├── vector_store.py       # ChromaDB storage + retrieval + source metadata
│   ├── rag_pipeline.py       # index_document() + query_rag() (separated phases)
│   ├── prompts.py            # All prompt templates + learning mode system
│   └── quiz_generator.py     # MCQ, interview, summary, project generation
│
└── data/
    ├── uploaded_pdfs/        # Per-user PDF storage
    └── users.db              # SQLite user accounts
```

---

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ai-learning-companion.git
cd ai-learning-companion

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at console.groq.com)

# 5. Run
streamlit run app.py
```

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push to GitHub (public or private repo)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App
3. Select your repo and set **Main file path** to `app.py`
4. Under **Advanced → Secrets**, add:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "your_key_here"
   ```
5. Click Deploy

---

## 🔑 Getting a Free API Key

| Provider | Free Tier | Link |
|----------|-----------|------|
| **Groq** | Very generous, fast | [console.groq.com](https://console.groq.com) |
| **Gemini** | 1M tokens/month | [aistudio.google.com](https://aistudio.google.com) |
| **OpenAI** | Paid | [platform.openai.com](https://platform.openai.com) |

---

## 🔮 Future Roadmap

- [ ] Voice input / text-to-speech answers
- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Flashcard generation (Anki export)
- [ ] Progress tracking & learning streaks
- [ ] Cloud database (Supabase/PostgreSQL)
- [ ] AI study plan generator
- [ ] Export chat history as PDF

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| LLM | Groq (Llama 3.1) / Gemini / OpenAI |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| PDF | PyMuPDF |
| Auth | SQLite + bcrypt |
| Deployment | Streamlit Community Cloud |

---

Built with ❤️ as an AI engineering portfolio project.
