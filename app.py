"""
AI Learning Companion
Main Streamlit application — production-ready AI study assistant
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config — MUST be first Streamlit call
st.set_page_config(
    page_title="AI Learning Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark, Modern, Professional
# ─────────────────────────────────────────────

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
  --bg-primary:    #0d0f14;
  --bg-secondary:  #13161e;
  --bg-card:       #181c27;
  --bg-hover:      #1e2333;
  --accent:        #6c63ff;
  --accent-2:      #00d4aa;
  --accent-warm:   #ff6b6b;
  --accent-yellow: #ffd166;
  --text-primary:  #e8eaf0;
  --text-muted:    #7c8499;
  --border:        #252a3a;
  --border-light:  #2e3447;
  --radius:        12px;
  --radius-lg:     18px;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Headings ── */
h1, h2, h3, h4 {
  font-family: 'Syne', sans-serif !important;
  color: var(--text-primary) !important;
}

/* ── Main header banner ── */
.app-header {
  background: linear-gradient(135deg, #1a1f35 0%, #0d1526 50%, #1a1335 100%);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 2rem 2.5rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.app-header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 50%, rgba(108,99,255,0.12) 0%, transparent 60%),
              radial-gradient(ellipse at 70% 50%, rgba(0,212,170,0.08) 0%, transparent 60%);
  pointer-events: none;
}
.app-header h1 {
  font-size: 2.2rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, #fff 30%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.4rem 0 !important;
}
.app-header p {
  color: var(--text-muted);
  font-size: 1rem;
  margin: 0;
  font-weight: 300;
}

/* ── Cards ── */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s, transform 0.2s;
}
.card:hover { border-color: var(--border-light); }

.card-accent {
  border-left: 3px solid var(--accent);
}
.card-green {
  border-left: 3px solid var(--accent-2);
}
.card-red {
  border-left: 3px solid var(--accent-warm);
}
.card-yellow {
  border-left: 3px solid var(--accent-yellow);
}

/* ── Stat badges ── */
.stat-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.stat-badge {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.6rem 1.1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.stat-badge span { color: var(--text-primary); font-weight: 600; }

/* ── Mode chips ── */
.mode-chip {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.mode-beginner  { background: rgba(0,212,170,0.15); color: var(--accent-2); }
.mode-exam      { background: rgba(108,99,255,0.15); color: var(--accent); }
.mode-practical { background: rgba(255,107,107,0.15); color: var(--accent-warm); }
.mode-interview { background: rgba(255,209,102,0.15); color: var(--accent-yellow); }

/* ── Section divider ── */
.section-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 1.5rem 0 0.75rem;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  margin-bottom: 0.75rem !important;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  padding: 0.5rem 1.2rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: white !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}

/* ── Select boxes ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--bg-card) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
  border-radius: 8px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--bg-secondary) !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  color: var(--text-muted) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  padding: 0.75rem 1.5rem !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom: 2px solid var(--accent) !important;
}

/* ── Info boxes ── */
[data-testid="stInfo"] {
  background: rgba(108,99,255,0.08) !important;
  border-left: 3px solid var(--accent) !important;
  border-radius: var(--radius) !important;
  color: var(--text-primary) !important;
}
[data-testid="stSuccess"] {
  background: rgba(0,212,170,0.08) !important;
  border-left: 3px solid var(--accent-2) !important;
}
[data-testid="stWarning"] {
  background: rgba(255,209,102,0.08) !important;
  border-left: 3px solid var(--accent-yellow) !important;
}
[data-testid="stError"] {
  background: rgba(255,107,107,0.08) !important;
  border-left: 3px solid var(--accent-warm) !important;
}

/* ── Sidebar labels ── */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
  color: var(--text-muted) !important;
  font-size: 0.85rem !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--bg-card) !important;
  border: 2px dashed var(--border-light) !important;
  border-radius: var(--radius) !important;
  padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
  border-radius: 4px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Weak topic alert ── */
.weak-alert {
  background: rgba(255,107,107,0.08);
  border: 1px solid rgba(255,107,107,0.3);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  margin-bottom: 0.75rem;
}
.weak-alert strong { color: var(--accent-warm); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

def init_session_state():
    defaults = {
        "chat_history": [],
        "uploaded_docs": [],
        "current_doc_text": "",
        "current_doc_name": "",
        "learning_mode": "Beginner",
        "question_log": [],
        "processing": False,
        "api_ready": False,
        "quiz_output": "",
        "summary_output": "",
        "project_output": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()


# ─────────────────────────────────────────────
# LAZY IMPORTS (after session init)
# ─────────────────────────────────────────────

from utils.pdf_loader import extract_text_from_pdf, save_uploaded_pdf, get_pdf_metadata
from utils.text_splitter import split_into_chunks
from utils.vector_store import store_chunks, retrieve_relevant_chunks, get_collection_stats, get_all_sources
from utils.gemini_api import generate_response, initialize_gemini, test_api_connection
from utils.prompts import build_rag_prompt, build_summary_prompt, build_project_recommendation_prompt, build_weak_topic_prompt
from utils.quiz_generator import generate_mcqs, generate_interview_questions, generate_short_answer_questions, format_quiz_for_display


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem; display:flex; align-items:center; gap:10px;'>
      <span style='font-size:1.6rem;'>🧠</span>
      <span style='font-family:Syne,sans-serif; font-size:1.1rem; font-weight:800; color:#e8eaf0;'>AI Learning<br>Companion</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ── API KEY ──
    st.markdown('<p class="section-label">🔑 API Configuration</p>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Get your free key at aistudio.google.com",
        placeholder="AIzaSy..."
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
    
    if st.button("🔌 Test Connection", use_container_width=True):
        with st.spinner("Testing..."):
            ok, msg = test_api_connection()
            if ok:
                st.success(msg)
                st.session_state.api_ready = True
            else:
                st.error(msg)
    
    st.divider()
    
    # ── LEARNING MODE ──
    st.markdown('<p class="section-label">🎓 Learning Mode</p>', unsafe_allow_html=True)
    mode_descriptions = {
        "Beginner":  "🌱 Simple explanations & analogies",
        "Exam":      "📝 Concise exam-ready answers",
        "Practical": "⚙️ Real-world implementations",
        "Interview": "💼 Interview prep & coaching",
    }
    selected_mode = st.selectbox(
        "Select mode",
        options=list(mode_descriptions.keys()),
        index=list(mode_descriptions.keys()).index(st.session_state.learning_mode),
        label_visibility="collapsed"
    )
    st.session_state.learning_mode = selected_mode
    st.caption(mode_descriptions[selected_mode])
    
    st.divider()
    
    # ── DOCUMENT LIBRARY ──
    st.markdown('<p class="section-label">📚 Document Library</p>', unsafe_allow_html=True)
    sources = get_all_sources()
    if sources:
        for src in sources:
            st.markdown(f"""
            <div style='background:#1e2333; border:1px solid #252a3a; border-radius:8px; 
                        padding:8px 12px; margin-bottom:6px; font-size:0.82rem; color:#7c8499;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>
              📄 {src}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No documents uploaded yet.")
    
    st.divider()
    
    # ── STATS ──
    stats = get_collection_stats()
    st.markdown(f"""
    <div class="stat-row" style="flex-direction:column; gap:0.5rem;">
      <div class="stat-badge">📦 Chunks stored: <span>{stats['total_chunks']}</span></div>
      <div class="stat-badge">📄 Documents: <span>{stats['total_documents']}</span></div>
      <div class="stat-badge">💬 Messages: <span>{len(st.session_state.chat_history)}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# App Header
st.markdown("""
<div class="app-header">
  <h1>🧠 AI Learning Companion</h1>
  <p>Upload your study material and learn smarter — chat, quiz, summarize, and build projects with AI</p>
</div>
""", unsafe_allow_html=True)

# ── TABS ──
tab_chat, tab_upload, tab_summary, tab_quiz, tab_projects, tab_weak = st.tabs([
    "💬 Chat", "📤 Upload", "📋 Summary", "❓ Quiz", "🚀 Projects", "🎯 Weak Topics"
])


# ═══════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════

with tab_chat:
    col_main, col_info = st.columns([3, 1])
    
    with col_main:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:1rem;'>
          <span style='font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700;'>Ask Your Documents</span>
          <span class='mode-chip mode-{selected_mode.lower()}'>{selected_mode} Mode</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat history display
        chat_container = st.container(height=420)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style='text-align:center; padding:3rem 1rem; color:#7c8499;'>
                  <div style='font-size:2.5rem; margin-bottom:1rem;'>💬</div>
                  <p style='font-size:1rem;'>No messages yet.</p>
                  <p style='font-size:0.85rem;'>Upload a PDF and start asking questions about it.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🧠"):
                        st.markdown(msg["content"])
        
        # Chat input
        user_query = st.chat_input("Ask anything about your uploaded documents...", key="chat_input")
        
        if user_query:
            if not os.getenv("GEMINI_API_KEY"):
                st.error("⚠️ Please add your Gemini API key in the sidebar.")
            else:
                # Log question for weak topic tracking
                st.session_state.question_log.append(user_query)
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                
                with st.spinner("🤔 Thinking..."):
                    # Retrieve relevant context
                    context_chunks = retrieve_relevant_chunks(user_query, n_results=5)
                    
                    if not context_chunks:
                        answer = (
                            "📭 No study material found in my memory. "
                            "Please upload a PDF first using the **Upload** tab."
                        )
                    else:
                        prompt = build_rag_prompt(
                            question=user_query,
                            context_chunks=context_chunks,
                            learning_mode=st.session_state.learning_mode,
                            chat_history=st.session_state.chat_history[:-1]
                        )
                        answer = generate_response(prompt)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                st.rerun()
    
    with col_info:
        st.markdown('<p class="section-label">💡 Quick Tips</p>', unsafe_allow_html=True)
        tips = [
            ("🎯", "Be specific", "Ask about a particular concept or chapter"),
            ("📖", "Reference pages", "Mention page numbers for precise answers"),
            ("🔄", "Change modes", "Switch learning mode in the sidebar"),
            ("📊", "Compare topics", "Ask to compare two concepts"),
        ]
        for icon, title, desc in tips:
            st.markdown(f"""
            <div class="card card-accent" style="padding:0.9rem;">
              <div style="font-size:1.2rem;">{icon}</div>
              <div style="font-weight:600; font-size:0.88rem; margin:4px 0;">{title}</div>
              <div style="color:#7c8499; font-size:0.78rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 2 — UPLOAD
# ═══════════════════════════════════════════════

with tab_upload:
    st.markdown('<p style="font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">Upload Study Material</p>', unsafe_allow_html=True)
    
    col_up, col_status = st.columns([3, 2])
    
    with col_up:
        uploaded_file = st.file_uploader(
            "Drop your PDF here",
            type=["pdf"],
            help="Upload lecture notes, textbooks, or any study material",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown(f"""
            <div class="card card-green">
              <div style="font-size:0.85rem; color:#7c8499; margin-bottom:4px;">Selected file</div>
              <div style="font-weight:600;">📄 {uploaded_file.name}</div>
              <div style="color:#7c8499; font-size:0.8rem; margin-top:4px;">
                {round(uploaded_file.size / 1024, 1)} KB
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⚡ Process & Index Document", use_container_width=True, type="primary"):
                progress_bar = st.progress(0, text="Saving file...")
                
                try:
                    # Step 1: Save
                    file_path = save_uploaded_pdf(uploaded_file)
                    progress_bar.progress(20, text="📄 Extracting text...")
                    
                    # Step 2: Extract text
                    text = extract_text_from_pdf(file_path)
                    progress_bar.progress(40, text="✂️ Splitting into chunks...")
                    
                    if len(text.strip()) < 100:
                        st.error("⚠️ Could not extract readable text from this PDF. Try a text-based (not scanned) PDF.")
                    else:
                        # Step 3: Split
                        chunks = split_into_chunks(text)
                        progress_bar.progress(60, text="🔢 Creating embeddings...")
                        
                        # Step 4 & 5: Embed + Store
                        stored = store_chunks(chunks, source_name=uploaded_file.name)
                        progress_bar.progress(90, text="💾 Indexing complete!")
                        
                        # Save to session
                        st.session_state.current_doc_text = text
                        st.session_state.current_doc_name = uploaded_file.name
                        if uploaded_file.name not in st.session_state.uploaded_docs:
                            st.session_state.uploaded_docs.append(uploaded_file.name)
                        
                        progress_bar.progress(100, text="✅ Ready!")
                        time.sleep(0.5)
                        progress_bar.empty()
                        
                        st.success(f"✅ **{uploaded_file.name}** indexed successfully!")
                        st.markdown(f"""
                        <div class="card card-green">
                          <div class="stat-row">
                            <div class="stat-badge">📝 Characters: <span>{len(text):,}</span></div>
                            <div class="stat-badge">🧩 Chunks: <span>{stored}</span></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error processing PDF: {str(e)}")
    
    with col_status:
        st.markdown('<p class="section-label">📚 Indexed Documents</p>', unsafe_allow_html=True)
        stats = get_collection_stats()
        
        if stats["sources"]:
            for src in stats["sources"]:
                st.markdown(f"""
                <div class="card">
                  <div style="font-size:0.85rem; font-weight:600; word-break:break-all;">📄 {src}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="card card-accent">
              <div style="font-size:0.8rem; color:#7c8499;">Total indexed</div>
              <div style="font-size:1.4rem; font-weight:800; color:#6c63ff;">{stats['total_chunks']}</div>
              <div style="font-size:0.75rem; color:#7c8499;">chunks across {stats['total_documents']} documents</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No documents indexed yet. Upload a PDF to get started.")
        
        st.markdown('<p class="section-label">📋 How It Works</p>', unsafe_allow_html=True)
        steps = ["📤 Upload PDF", "📝 Extract text", "✂️ Split into chunks",
                 "🔢 Create embeddings", "💾 Store in ChromaDB", "💬 Ready to chat!"]
        for i, step in enumerate(steps):
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:5px 0; font-size:0.82rem; color:#7c8499;">
              <span style="background:#252a3a; border-radius:50%; width:22px; height:22px; 
                           display:flex; align-items:center; justify-content:center; 
                           font-size:0.7rem; flex-shrink:0;">{i+1}</span>
              {step}
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 3 — SUMMARY
# ═══════════════════════════════════════════════

with tab_summary:
    st.markdown('<p style="font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">Document Summarization</p>', unsafe_allow_html=True)
    
    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first to generate summaries.")
    else:
        st.markdown(f"""
        <div class="card card-accent" style="padding:0.8rem 1.2rem;">
          <span style="color:#7c8499; font-size:0.82rem;">Active document:</span>
          <strong style="margin-left:8px;">📄 {st.session_state.current_doc_name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            if st.button("📋 Chapter Summary", use_container_width=True):
                with st.spinner("Generating summary..."):
                    prompt = build_summary_prompt(st.session_state.current_doc_text, "chapter")
                    st.session_state.summary_output = generate_response(prompt)
                    st.session_state.summary_type = "chapter"
        
        with col_s2:
            if st.button("⚡ Quick Revision", use_container_width=True):
                with st.spinner("Creating cheat sheet..."):
                    prompt = build_summary_prompt(st.session_state.current_doc_text, "quick")
                    st.session_state.summary_output = generate_response(prompt)
                    st.session_state.summary_type = "quick"
        
        with col_s3:
            if st.button("🌱 Simplify Topic", use_container_width=True):
                with st.spinner("Simplifying..."):
                    prompt = build_summary_prompt(st.session_state.current_doc_text, "simplify")
                    st.session_state.summary_output = generate_response(prompt)
                    st.session_state.summary_type = "simplify"
        
        if st.session_state.summary_output:
            st.divider()
            st.markdown(st.session_state.summary_output)
            
            # Copy button
            st.download_button(
                "⬇️ Download Summary",
                data=st.session_state.summary_output,
                file_name=f"summary_{st.session_state.current_doc_name}.txt",
                mime="text/plain",
                use_container_width=True
            )


# ═══════════════════════════════════════════════
# TAB 4 — QUIZ
# ═══════════════════════════════════════════════

with tab_quiz:
    st.markdown('<p style="font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">Quiz Generator</p>', unsafe_allow_html=True)
    
    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first to generate quizzes.")
    else:
        col_q1, col_q2 = st.columns([1, 2])
        
        with col_q1:
            num_q = st.slider("Number of questions", 3, 10, 5)
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔵 MCQ Quiz", use_container_width=True):
                with st.spinner("Generating MCQs..."):
                    raw = generate_mcqs(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw, "mcq")
        
        with col_btn2:
            if st.button("💼 Interview Qs", use_container_width=True):
                with st.spinner("Generating interview questions..."):
                    raw = generate_interview_questions(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw, "interview")
        
        with col_btn3:
            if st.button("📝 Short Answer", use_container_width=True):
                with st.spinner("Generating practice questions..."):
                    raw = generate_short_answer_questions(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw, "short")
        
        if st.session_state.quiz_output:
            st.divider()
            st.markdown(st.session_state.quiz_output)
            
            st.download_button(
                "⬇️ Download Quiz",
                data=st.session_state.quiz_output,
                file_name=f"quiz_{st.session_state.current_doc_name}.txt",
                mime="text/plain",
                use_container_width=True
            )


# ═══════════════════════════════════════════════
# TAB 5 — PROJECT RECOMMENDATIONS
# ═══════════════════════════════════════════════

with tab_projects:
    st.markdown('<p style="font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">AI Project Recommendations</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499; font-size:0.9rem; margin-bottom:1.5rem;">Get AI-powered project ideas based on your study material to build a portfolio.</p>', unsafe_allow_html=True)
    
    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first to get project recommendations.")
    else:
        if st.button("🚀 Generate Project Ideas", use_container_width=True, type="primary"):
            with st.spinner("Brainstorming project ideas..."):
                prompt = build_project_recommendation_prompt(st.session_state.current_doc_text)
                st.session_state.project_output = generate_response(prompt)
        
        if st.session_state.project_output:
            st.divider()
            st.markdown(st.session_state.project_output)


# ═══════════════════════════════════════════════
# TAB 6 — WEAK TOPICS
# ═══════════════════════════════════════════════

with tab_weak:
    st.markdown('<p style="font-family:Syne,sans-serif; font-size:1.2rem; font-weight:700; margin-bottom:1rem;">Weak Topic Detection</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499; font-size:0.9rem;">Analyzes your questions to detect topics you need to revise more.</p>', unsafe_allow_html=True)
    
    question_log = st.session_state.question_log
    
    if len(question_log) < 3:
        st.info(f"💬 Ask at least 3 questions in the chat to enable weak topic detection. ({len(question_log)}/3 so far)")
    else:
        st.markdown(f"""
        <div class="card card-yellow">
          <div style="font-size:0.82rem; color:#7c8499;">Questions analyzed</div>
          <div style="font-size:1.6rem; font-weight:800; color:#ffd166;">{len(question_log)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📝 View Your Question History"):
            for i, q in enumerate(question_log, 1):
                st.markdown(f"`{i}.` {q}")
        
        if st.button("🎯 Analyze Weak Topics", use_container_width=True, type="primary"):
            with st.spinner("Analyzing your learning patterns..."):
                prompt = build_weak_topic_prompt(question_log)
                analysis = generate_response(prompt)
            
            st.divider()
            st.markdown(analysis)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div style='text-align:center; padding:2rem 0 1rem; color:#3d4257; font-size:0.78rem;'>
  Built with Streamlit · Gemini API · ChromaDB · sentence-transformers
</div>
""", unsafe_allow_html=True)

