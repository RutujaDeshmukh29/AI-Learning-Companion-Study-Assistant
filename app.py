"""
AI Learning Companion — Main Application
==========================================
Architecture decisions:
- Auth check runs first (before any feature renders).
- Session state is initialised once and never reset mid-session.
- Indexing (PDF processing) is separated from querying (chat).
  query_rag() is called on every message; index_document() only on upload.
- All AI generation (summary, quiz, projects) goes through quiz_generator.py
  which proxies to llm.py -> provider-agnostic.
- UI state (selected mode, current doc, outputs) lives in st.session_state
  so reruns don't lose user context.
"""

import streamlit as st
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="AI Learning Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{
  --bg:       #0d0f14;
  --bg2:      #13161e;
  --card:     #181c27;
  --hover:    #1e2333;
  --accent:   #6c63ff;
  --green:    #00d4aa;
  --red:      #ff6b6b;
  --yellow:   #ffd166;
  --txt:      #e8eaf0;
  --muted:    #7c8499;
  --border:   #252a3a;
  --border2:  #2e3447;
  --r:        12px;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--txt);font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stToolbar"]{display:none;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--txt)!important;}
.app-header{background:linear-gradient(135deg,#1a1f35,#0d1526,#1a1335);border:1px solid var(--border2);border-radius:18px;padding:1.8rem 2.2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.app-header::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(108,99,255,.12),transparent 60%),radial-gradient(ellipse at 70% 50%,rgba(0,212,170,.08),transparent 60%);pointer-events:none;}
.app-header h1{font-size:2rem!important;font-weight:800!important;background:linear-gradient(135deg,#fff 30%,var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 .3rem!important;}
.app-header p{color:var(--muted);font-size:.9rem;margin:0;}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:1.2rem;margin-bottom:.8rem;}
.card-a{border-left:3px solid var(--accent);}
.card-g{border-left:3px solid var(--green);}
.card-r{border-left:3px solid var(--red);}
.card-y{border-left:3px solid var(--yellow);}
.sec{font-family:'Syne',sans-serif;font-size:.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:1.2rem 0 .6rem;}
.badge{background:var(--hover);border:1px solid var(--border);border-radius:7px;padding:.45rem .9rem;font-size:.82rem;color:var(--muted);display:inline-flex;align-items:center;gap:.4rem;margin:.2rem;}
.badge b{color:var(--txt);}
.chip{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:600;letter-spacing:.03em;}
.chip-b{background:rgba(0,212,170,.15);color:var(--green);}
.chip-e{background:rgba(108,99,255,.15);color:var(--accent);}
.chip-p{background:rgba(255,107,107,.15);color:var(--red);}
.chip-i{background:rgba(255,209,102,.15);color:var(--yellow);}
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;margin-bottom:.6rem!important;}
.stButton>button{background:var(--hover)!important;color:var(--txt)!important;border:1px solid var(--border2)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-weight:500!important;transition:all .2s!important;}
.stButton>button:hover{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important;}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;border-color:var(--border)!important;color:var(--txt)!important;border-radius:8px!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:var(--bg2)!important;border-bottom:1px solid var(--border)!important;}
[data-testid="stTabs"] [data-baseweb="tab"]{color:var(--muted)!important;font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.88rem!important;}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}
[data-testid="stFileUploader"]{background:var(--card)!important;border:2px dashed var(--border2)!important;border-radius:var(--r)!important;}
[data-testid="stInfo"]{background:rgba(108,99,255,.08)!important;border-left:3px solid var(--accent)!important;border-radius:var(--r)!important;}
[data-testid="stSuccess"]{background:rgba(0,212,170,.08)!important;border-left:3px solid var(--green)!important;}
[data-testid="stWarning"]{background:rgba(255,209,102,.08)!important;border-left:3px solid var(--yellow)!important;}
[data-testid="stError"]{background:rgba(255,107,107,.08)!important;border-left:3px solid var(--red)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}
</style>
""", unsafe_allow_html=True)


# ── Auth ──────────────────────────────────────────────────────────────────────
from auth.auth_manager import init_db, is_authenticated, logout, get_current_user, get_user_upload_dir
from auth.auth_ui      import show_auth_page

init_db()

if not is_authenticated():
    show_auth_page()
    st.stop()   # nothing below renders until logged in


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "messages":          [],
        "uploaded_docs":     [],
        "current_doc_text":  "",
        "current_doc_name":  "",
        "learning_mode":     "Beginner",
        "question_log":      [],
        "quiz_output":       "",
        "summary_output":    "",
        "project_output":    "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

user = get_current_user()

# ── Lazy imports (after session init) ────────────────────────────────────────
from utils.pdf_loader     import extract_text_from_pdf
from utils.text_splitter  import split_text
from utils.vector_store   import get_collection_stats, get_all_sources, delete_source
from utils.rag_pipeline   import index_document, query_rag
from utils.llm            import get_provider_info, test_llm_connection
from utils.quiz_generator import (
    generate_mcqs, generate_interview_questions, generate_short_answer_questions,
    generate_summary, generate_project_recommendations, generate_weak_topic_analysis,
    format_quiz_for_display,
)


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── user badge ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='padding:.8rem 0 .5rem;display:flex;align-items:center;gap:10px;'>
      <div style='width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#6c63ff,#00d4aa);
                  display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:700;color:#fff;'>
        {user["username"][0].upper()}
      </div>
      <div>
        <div style='font-family:Syne,sans-serif;font-weight:700;font-size:.95rem;'>{user["username"]}</div>
        <div style='color:#7c8499;font-size:.75rem;'>{user["email"]}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    st.divider()

    # ── API key & connection test ────────────────────────────────────────────
    st.markdown('<p class="sec">🔑 LLM Configuration</p>', unsafe_allow_html=True)
    info = get_provider_info()
    st.caption(f"Provider: **{info['provider'].upper()}** | Model: `{info['model']}`")

    api_key = st.text_input(
        "API Key", type="password",
        value=os.getenv("GROQ_API_KEY", "") or os.getenv("GEMINI_API_KEY", ""),
        placeholder="paste your API key...",
        help="Set in .env or paste here. Stored only for this session.",
    )
    if api_key:
        provider = info["provider"]
        if provider == "groq":
            os.environ["GROQ_API_KEY"] = api_key
        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = api_key
        elif provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key

    if st.button("🔌 Test Connection", use_container_width=True):
        with st.spinner("Testing..."):
            ok, msg = test_llm_connection()
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.divider()

    # ── Learning mode ────────────────────────────────────────────────────────
    st.markdown('<p class="sec">🎓 Learning Mode</p>', unsafe_allow_html=True)
    MODE_LABELS = {
        "Beginner":  "🌱 Simple & friendly explanations",
        "Exam":      "📝 Concise exam-ready answers",
        "Practical": "⚙️ Real-world implementations",
        "Interview": "💼 Interview prep coaching",
    }
    mode = st.selectbox("Mode", list(MODE_LABELS.keys()),
                        index=list(MODE_LABELS.keys()).index(st.session_state.learning_mode),
                        label_visibility="collapsed")
    st.session_state.learning_mode = mode
    st.caption(MODE_LABELS[mode])

    st.divider()

    # ── Document library ─────────────────────────────────────────────────────
    st.markdown('<p class="sec">📚 Indexed Documents</p>', unsafe_allow_html=True)
    sources = get_all_sources()
    if sources:
        for src in sources:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"<div style='font-size:.8rem;color:#7c8499;padding:4px 0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;' title='{src}'>📄 {src}</div>", unsafe_allow_html=True)
            if c2.button("✕", key=f"del_{src}", help=f"Remove {src}"):
                delete_source(src)
                if st.session_state.current_doc_name == src:
                    st.session_state.current_doc_name = ""
                    st.session_state.current_doc_text = ""
                st.rerun()
    else:
        st.caption("No documents yet.")

    st.divider()

    # ── Stats ─────────────────────────────────────────────────────────────────
    stats = get_collection_stats()
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;gap:.4rem;'>
      <span class='badge'>📦 Chunks <b>{stats['total_chunks']}</b></span>
      <span class='badge'>📄 Docs <b>{stats['total_documents']}</b></span>
      <span class='badge'>💬 Messages <b>{len(st.session_state.messages)}</b></span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
chip_class = {"Beginner":"chip-b","Exam":"chip-e","Practical":"chip-p","Interview":"chip-i"}[mode]

st.markdown(f"""
<div class='app-header'>
  <div style='display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:.5rem;'>
    <div>
      <h1>🧠 AI Learning Companion</h1>
      <p>Upload study material · Chat · Summarise · Quiz · Build projects</p>
    </div>
    <span class='chip {chip_class}' style='margin-top:.5rem;'>{mode} Mode</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
t_chat, t_upload, t_summary, t_quiz, t_projects, t_weak = st.tabs([
    "💬 Chat", "📤 Upload", "📋 Summary", "❓ Quiz", "🚀 Projects", "🎯 Weak Topics"
])


# ── TAB: CHAT ─────────────────────────────────────────────────────────────────
with t_chat:
    col_chat, col_tips = st.columns([3, 1])

    with col_chat:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:1rem;'>
          <span style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;'>Chat with your documents</span>
          <span class='chip {chip_class}'>{mode}</span>
        </div>
        """, unsafe_allow_html=True)

        chat_box = st.container(height=430)
        with chat_box:
            if not st.session_state.messages:
                st.markdown("""
                <div style='text-align:center;padding:3rem 1rem;color:#7c8499;'>
                  <div style='font-size:2.5rem;margin-bottom:.8rem;'>💬</div>
                  <p>No messages yet.<br>Upload a PDF and ask away!</p>
                </div>
                """, unsafe_allow_html=True)
            for msg in st.session_state.messages:
                avatar = f"🧑‍💻" if msg["role"] == "user" else "🧠"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

        user_input = st.chat_input(f"Ask anything about your documents... ({mode} mode)")

        if user_input:
            st.session_state.question_log.append(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("Thinking..."):
                answer, _ = query_rag(
                    question=user_input,
                    top_k=5,
                    learning_mode=st.session_state.learning_mode,
                    chat_history=st.session_state.messages[:-1],
                    username=user["username"],
                )

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

    with col_tips:
        st.markdown('<p class="sec">💡 Tips</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("🎯", "Be specific", "Ask about a particular concept"),
            ("📖", "Mention pages", "E.g. 'What's on page 5?'"),
            ("🔄", "Follow up", "Ask 'Can you explain more?'"),
            ("📊", "Compare", "Ask to compare two concepts"),
        ]:
            st.markdown(f"""
            <div class='card card-a' style='padding:.8rem;'>
              <div style='font-size:1.1rem;'>{icon}</div>
              <div style='font-weight:600;font-size:.85rem;margin:3px 0;'>{title}</div>
              <div style='color:#7c8499;font-size:.75rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ── TAB: UPLOAD ───────────────────────────────────────────────────────────────
with t_upload:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:1rem;">Upload Study Material</p>', unsafe_allow_html=True)

    col_up, col_status = st.columns([3, 2])

    with col_up:
        uploaded = st.file_uploader("Drop PDF here", type=["pdf"], label_visibility="collapsed")

        if uploaded:
            st.markdown(f"""
            <div class='card card-g'>
              <div style='font-size:.8rem;color:#7c8499;'>Selected</div>
              <div style='font-weight:600;margin-top:3px;'>📄 {uploaded.name}</div>
              <div style='color:#7c8499;font-size:.78rem;margin-top:2px;'>{round(uploaded.size/1024,1)} KB</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ Process & Index", use_container_width=True, type="primary"):
                prog = st.progress(0, "Saving file...")
                try:
                    upload_dir = get_user_upload_dir(user["username"])
                    file_path  = os.path.join(upload_dir, uploaded.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    prog.progress(30, "📄 Extracting & chunking...")

                    result = index_document(file_path, source_name=uploaded.name)
                    prog.progress(90, "💾 Finalising...")
                    time.sleep(0.3)
                    prog.progress(100, "✅ Done!")
                    time.sleep(0.4)
                    prog.empty()

                    if result["success"]:
                        # Read text for summary/quiz tabs
                        st.session_state.current_doc_text = extract_text_from_pdf(file_path)
                        st.session_state.current_doc_name = uploaded.name
                        if uploaded.name not in st.session_state.uploaded_docs:
                            st.session_state.uploaded_docs.append(uploaded.name)
                        st.success(f"✅ **{uploaded.name}** indexed — {result['chunks']} chunks stored.")
                    else:
                        st.error(f"❌ {result['error']}")

                except Exception as e:
                    prog.empty()
                    st.error(f"❌ Error: {str(e)}")

        st.markdown('<p class="sec" style="margin-top:1.5rem;">⚙️ How indexing works</p>', unsafe_allow_html=True)
        for i, step in enumerate(["Upload PDF","Extract text","Sentence-aware chunking",
                                   "Generate embeddings","Store in ChromaDB","Ready to chat ✅"], 1):
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;padding:4px 0;font-size:.8rem;color:#7c8499;'>
              <span style='background:#252a3a;border-radius:50%;width:20px;height:20px;display:flex;
                           align-items:center;justify-content:center;font-size:.68rem;flex-shrink:0;'>{i}</span>
              {step}
            </div>
            """, unsafe_allow_html=True)

    with col_status:
        st.markdown('<p class="sec">📚 Indexed Documents</p>', unsafe_allow_html=True)
        stats = get_collection_stats()
        if stats["sources"]:
            for src in stats["sources"]:
                active = src == st.session_state.current_doc_name
                border = "var(--accent)" if active else "var(--border)"
                st.markdown(f"""
                <div class='card' style='border-color:{border};padding:.8rem;'>
                  <div style='font-size:.82rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>📄 {src}</div>
                  {"<div style='font-size:.7rem;color:var(--accent);margin-top:2px;'>● active</div>" if active else ""}
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class='card card-a' style='padding:.8rem;margin-top:.5rem;'>
              <div style='font-size:.75rem;color:#7c8499;'>Total indexed</div>
              <div style='font-size:1.6rem;font-weight:800;color:var(--accent);'>{stats['total_chunks']}</div>
              <div style='font-size:.72rem;color:#7c8499;'>chunks · {stats['total_documents']} docs</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No documents indexed yet.")


# ── TAB: SUMMARY ──────────────────────────────────────────────────────────────
with t_summary:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.5rem;">Document Summarisation</p>', unsafe_allow_html=True)

    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first.")
    else:
        st.markdown(f"<div class='card card-a' style='padding:.7rem 1rem;font-size:.85rem;'>Active: <strong>📄 {st.session_state.current_doc_name}</strong></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if c1.button("📋 Chapter Summary",  use_container_width=True):
            with st.spinner("Summarising..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text, "chapter")
        if c2.button("⚡ Quick Cheat Sheet", use_container_width=True):
            with st.spinner("Building cheat sheet..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text, "quick")
        if c3.button("🌱 Simplify for Me",   use_container_width=True):
            with st.spinner("Simplifying..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text, "simplify")

        if st.session_state.summary_output:
            st.divider()
            st.markdown(st.session_state.summary_output)
            st.download_button("⬇️ Download", data=st.session_state.summary_output,
                               file_name=f"summary_{st.session_state.current_doc_name}.txt",
                               use_container_width=True)


# ── TAB: QUIZ ─────────────────────────────────────────────────────────────────
with t_quiz:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.5rem;">Quiz Generator</p>', unsafe_allow_html=True)

    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first.")
    else:
        num_q = st.slider("Number of questions", 3, 10, 5)
        c1, c2, c3 = st.columns(3)
        if c1.button("🔵 MCQ Quiz",       use_container_width=True):
            with st.spinner("Generating MCQs..."):
                raw = generate_mcqs(st.session_state.current_doc_text, num_q)
                st.session_state.quiz_output = format_quiz_for_display(raw, "mcq")
        if c2.button("💼 Interview Qs",   use_container_width=True):
            with st.spinner("Generating interview questions..."):
                raw = generate_interview_questions(st.session_state.current_doc_text, num_q)
                st.session_state.quiz_output = format_quiz_for_display(raw, "interview")
        if c3.button("📝 Short Answer",   use_container_width=True):
            with st.spinner("Generating practice questions..."):
                raw = generate_short_answer_questions(st.session_state.current_doc_text, num_q)
                st.session_state.quiz_output = format_quiz_for_display(raw, "short")

        if st.session_state.quiz_output:
            st.divider()
            st.markdown(st.session_state.quiz_output)
            st.download_button("⬇️ Download Quiz", data=st.session_state.quiz_output,
                               file_name=f"quiz_{st.session_state.current_doc_name}.txt",
                               use_container_width=True)


# ── TAB: PROJECTS ─────────────────────────────────────────────────────────────
with t_projects:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.3rem;">AI Project Recommendations</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499;font-size:.88rem;margin-bottom:1rem;">Get portfolio-worthy project ideas based on your study material.</p>', unsafe_allow_html=True)

    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first.")
    else:
        if st.button("🚀 Generate Project Ideas", use_container_width=True, type="primary"):
            with st.spinner("Brainstorming ideas..."):
                st.session_state.project_output = generate_project_recommendations(st.session_state.current_doc_text)
        if st.session_state.project_output:
            st.divider()
            st.markdown(st.session_state.project_output)


# ── TAB: WEAK TOPICS ──────────────────────────────────────────────────────────
with t_weak:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.3rem;">Weak Topic Detection</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499;font-size:.88rem;margin-bottom:1rem;">Analyses your question history to surface concepts you should revisit.</p>', unsafe_allow_html=True)

    q_log = st.session_state.question_log
    if len(q_log) < 3:
        st.info(f"💬 Ask at least 3 questions in Chat to enable this feature. ({len(q_log)}/3)")
    else:
        st.markdown(f"""<span class='badge'>🧮 Questions analysed: <b>{len(q_log)}</b></span>""", unsafe_allow_html=True)
        with st.expander("📝 View question history"):
            for i, q in enumerate(q_log, 1):
                st.markdown(f"`{i}.` {q}")

        if st.button("🎯 Analyse Weak Topics", use_container_width=True, type="primary"):
            with st.spinner("Analysing learning patterns..."):
                analysis = generate_weak_topic_analysis(q_log)
            st.divider()
            st.markdown(analysis)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 .5rem;color:#2a2f3f;font-size:.75rem;'>
  AI Learning Companion · Streamlit + ChromaDB + sentence-transformers
</div>
""", unsafe_allow_html=True)
