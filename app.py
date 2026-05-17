"""
AI Learning Companion  —  v3 Production
=========================================
New in v3 (all additive, nothing removed):
  - 8 tabs: Chat | Upload | Summary | Quiz | Roadmap | Diagrams | Dashboard | History
  - Persistent chat history (SQLite) per user per session
  - Roadmap generation + progress tracking with checkboxes
  - Mermaid diagram generation (flowchart / mindmap / sequence / class)
  - Learning analytics dashboard (streak, topics, activity, mode distribution)
  - Voice input + TTS output via browser Web Speech API
  - Study day plan generator
  - Coding challenge generator
  - Session history browser — load any past conversation
  - Saved outputs library (quizzes, summaries, roadmaps, diagrams)
  - Hybrid RAG responses (doc-grounded + AI expansion)
  - All 6 learning modes with per-mode chip colours
"""

import streamlit as st
import streamlit.components.v1 as components
import os, time
from dotenv import load_dotenv

load_dotenv()

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
  --bg:#0d0f14; --bg2:#13161e; --card:#181c27; --hover:#1e2333;
  --accent:#6c63ff; --green:#00d4aa; --red:#ff6b6b; --yellow:#ffd166;
  --orange:#ff9a3c; --teal:#00b4d8; --txt:#e8eaf0; --muted:#7c8499;
  --border:#252a3a; --border2:#2e3447; --r:12px;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--txt);font-family:'DM Sans',sans-serif;}
div.block-container{padding:1.5rem 1rem 2rem!important;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer{visibility:hidden;}header{visibility:visible!important;height:0!important;min-height:0!important;}[data-testid="stDeployButton"]{display:none;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--txt)!important;}

/* ── Header ── */
.app-header{background:linear-gradient(135deg,#1a1f35,#0d1526,#1a1335);border:1px solid var(--border2);border-radius:18px;padding:1.6rem 2rem;margin-bottom:1.2rem;position:sticky;top:-24px;z-index:999;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);background:rgba(13,15,20,.8);}
.app-header::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 25% 50%,rgba(108,99,255,.15),transparent 55%),radial-gradient(ellipse at 75% 50%,rgba(0,212,170,.1),transparent 55%);pointer-events:none;}
.app-header h1{font-size:1.9rem!important;font-weight:800!important;background:linear-gradient(135deg,#fff 40%,var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 .25rem!important;}
.app-header p{color:var(--muted);font-size:.85rem;margin:0;}

/* ── Cards ── */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:1.1rem;margin-bottom:.7rem;}
.card-a{border-left:3px solid var(--accent);} .card-g{border-left:3px solid var(--green);}
.card-r{border-left:3px solid var(--red);}    .card-y{border-left:3px solid var(--yellow);}
.card-o{border-left:3px solid var(--orange);} .card-t{border-left:3px solid var(--teal);}

/* ── Chips / Badges ── */
.chip{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:600;letter-spacing:.03em;}
.chip-green {background:rgba(0,212,170,.15);color:var(--green);}
.chip-purple{background:rgba(108,99,255,.15);color:var(--accent);}
.chip-orange{background:rgba(255,154,60,.15); color:var(--orange);}
.chip-blue  {background:rgba(0,180,216,.15);  color:var(--teal);}
.chip-teal  {background:rgba(0,180,216,.15);  color:var(--teal);}
.chip-yellow{background:rgba(255,209,102,.15);color:var(--yellow);}
.badge{background:var(--hover);border:1px solid var(--border);border-radius:7px;padding:.4rem .8rem;font-size:.8rem;color:var(--muted);display:inline-flex;align-items:center;gap:.35rem;margin:.15rem;}
.badge b{color:var(--txt);}
.sec{font-family:'Syne',sans-serif;font-size:.66rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:1rem 0 .5rem;}

/* ── Stat cards ── */
.stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem;margin-bottom:1rem;}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.9rem;text-align:center;}
.stat-card .num{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;line-height:1;}
.stat-card .lbl{font-size:.72rem;color:var(--muted);margin-top:3px;}

/* ── Chat ── */
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;margin-bottom:.5rem!important;}

/* ── Buttons ── */
.stButton>button{background:var(--hover)!important;color:var(--txt)!important;border:1px solid var(--border2)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-weight:500!important;transition:all .18s!important;}
.stButton>button:hover{background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important;}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;border-color:var(--border)!important;color:var(--txt)!important;border-radius:8px!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:var(--bg2)!important;border-bottom:1px solid var(--border)!important;}
[data-testid="stTabs"] [data-baseweb="tab"]{color:var(--muted)!important;font-family:'Syne',sans-serif!important;font-weight:600!important;font-size:.82rem!important;padding:.65rem 1rem!important;}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent)!important;border-bottom:2px solid var(--accent)!important;}
[data-testid="stFileUploader"]{background:var(--card)!important;border:2px dashed var(--border2)!important;border-radius:var(--r)!important;}
[data-testid="stInfo"]{background:rgba(108,99,255,.08)!important;border-left:3px solid var(--accent)!important;border-radius:var(--r)!important;}
[data-testid="stSuccess"]{background:rgba(0,212,170,.08)!important;border-left:3px solid var(--green)!important;}
[data-testid="stWarning"]{background:rgba(255,209,102,.08)!important;border-left:3px solid var(--yellow)!important;}
[data-testid="stError"]{background:rgba(255,107,107,.08)!important;border-left:3px solid var(--red)!important;}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;}
::-webkit-scrollbar{width:5px;} ::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}
input[type="checkbox"]{accent-color:var(--accent);}
</style>
""", unsafe_allow_html=True)


# ── Auth guard ────────────────────────────────────────────────────────────────
from auth.auth_manager import init_db, is_authenticated, logout, get_current_user, get_user_upload_dir
from auth.auth_ui      import show_auth_page

init_db()
if not is_authenticated():
    show_auth_page()
    st.stop()


# ── DB table init ─────────────────────────────────────────────────────────────
from utils.history   import init_history_tables
from utils.roadmap   import init_roadmap_table
init_history_tables()
init_roadmap_table()


# ── Session state ─────────────────────────────────────────────────────────────
user = get_current_user()

def _init():
    defaults = {
        "messages":         [],
        "current_doc_text": "",
        "current_doc_name": "",
        "learning_mode":    "Beginner",
        "question_log":     [],
        "quiz_output":      "",
        "summary_output":   "",
        "project_output":   "",
        "roadmap_output":   "",
        "roadmap_id":       None,
        "roadmap_phases":   [],
        "diagram_code":     "",
        "voice_enabled":    False,
        "hybrid_mode":      True,
        "session_id":       None,
        "challenge_output": "",
        "study_plan_output":"",
        "active_sources":   [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ── Lazy imports ──────────────────────────────────────────────────────────────
from utils.pdf_loader    import extract_text_from_pdf
from utils.vector_store  import get_collection_stats, get_all_sources, delete_source
from utils.rag_pipeline  import index_document, query_rag
from utils.llm           import get_provider_info, test_llm_connection
from utils.quiz_generator import (
    generate_mcqs, generate_interview_questions, generate_short_answer_questions,
    generate_summary, generate_project_recommendations, generate_weak_topic_analysis,
    format_quiz_for_display,
)
from utils.prompts   import LEARNING_MODES, get_mode_meta, build_coding_challenge_prompt
from utils.roadmap   import (
    generate_roadmap, generate_study_plan, save_roadmap,
    load_latest_roadmap, load_all_roadmaps, get_progress,
    get_completion_percentage, mark_topic_complete,
)
from utils.diagram   import generate_diagram, mermaid_to_html, DIAGRAM_TYPES
from utils.analytics import get_dashboard_data
from utils.history   import (
    get_or_create_session, save_message, load_messages,
    list_sessions, load_saved_outputs, save_output, delete_session,
)
from utils.voice     import get_voice_input_html, get_tts_html
from utils.llm       import ask_llm


# ── Helpers ───────────────────────────────────────────────────────────────────
mode     = st.session_state.learning_mode
mode_cfg = get_mode_meta(mode)
chip_cls = mode_cfg["chip_class"]


def ensure_session():
    """Lazily create/load today's DB session for this user+doc."""
    if not st.session_state.session_id:
        sid = get_or_create_session(
            user["id"],
            st.session_state.current_doc_name,
            mode,
        )
        st.session_state.session_id = sid
        existing = load_messages(sid)
        if existing and not st.session_state.messages:
            st.session_state.messages = existing
    return st.session_state.session_id


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── user ─────────────────────────────────────────────────────────────────
    initials = user["username"][0].upper()
    st.markdown(f"""
    <div style='padding:.6rem 0 .4rem;display:flex;align-items:center;gap:10px;'>
      <div style='width:36px;height:36px;border-radius:50%;
                  background:linear-gradient(135deg,#6c63ff,#00d4aa);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem;font-weight:800;color:#fff;flex-shrink:0;'>{initials}</div>
      <div>
        <div style='font-family:Syne,sans-serif;font-weight:700;font-size:.92rem;'>{user["username"]}</div>
        <div style='color:#7c8499;font-size:.72rem;'>{user["email"]}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    st.divider()



    # ── Learning mode ─────────────────────────────────────────────────────────
    st.markdown('<p class="sec">🎓 Learning Mode</p>', unsafe_allow_html=True)
    mode_options = list(LEARNING_MODES.keys())
    mode_labels  = [f"{LEARNING_MODES[m]['emoji']} {m}" for m in mode_options]
    sel_idx      = mode_options.index(st.session_state.learning_mode)
    sel          = st.selectbox("Mode", mode_labels, index=sel_idx, label_visibility="collapsed")
    new_mode     = mode_options[mode_labels.index(sel)]

    if new_mode != st.session_state.learning_mode:
        st.session_state.learning_mode = new_mode
        st.session_state.session_id    = None   # new session for mode change
        st.rerun()

    st.caption(LEARNING_MODES[new_mode]["description"])

    st.divider()

    # ── Settings ──────────────────────────────────────────────────────────────
    st.markdown('<p class="sec">⚙️ Settings</p>', unsafe_allow_html=True)
    st.session_state.hybrid_mode  = st.toggle("🔀 Hybrid RAG (doc + AI expansion)", value=st.session_state.hybrid_mode)
    st.session_state.voice_enabled = st.toggle("🔊 Voice Output (TTS)", value=st.session_state.voice_enabled)

    st.divider()

    # ── Docs ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="sec">📚 Indexed Docs</p>', unsafe_allow_html=True)
    sources = get_all_sources()

    # Sync sources with session state, activating new docs by default
    if not sources:
        st.session_state.active_sources = []
    elif "active_sources" not in st.session_state:
        st.session_state.active_sources = list(sources)
    else:
        # Prune deleted sources from active list
        st.session_state.active_sources = [s for s in st.session_state.active_sources if s in sources]
        # Add newly uploaded sources to active list
        for s in sources:
            if s not in st.session_state.active_sources:
                st.session_state.active_sources.append(s)

    if sources:
        st.markdown('<p style="font-size: .8rem; color: var(--muted); margin-bottom: .5rem;">Select sources for chat:</p>', unsafe_allow_html=True)
        
        # Collect checkbox states
        new_active_sources = []
        for src in sources:
            c1, c2 = st.columns([4,1])
            is_active = src in st.session_state.active_sources
            if c1.checkbox(src, value=is_active, key=f"cb_{src}"):
                new_active_sources.append(src)
            
            if c2.button("✕", key=f"del_{src}", help=f"Remove {src}"):
                delete_source(src)
                st.rerun()
        st.session_state.active_sources = new_active_sources

        c1, c2 = st.columns(2)
        if c1.button("Select All", use_container_width=True):
            st.session_state.active_sources = list(sources)
            st.rerun()
        if c2.button("Deselect All", use_container_width=True):
            st.session_state.active_sources = []
            st.rerun()

        st.divider()

        # UI for selecting the primary document for single-doc features
        st.markdown('<p style="font-size: .8rem; color: var(--muted);">Select primary for Summary/Quiz:</p>', unsafe_allow_html=True)
        
        current_doc_index = 0
        if st.session_state.current_doc_name in sources:
            current_doc_index = sources.index(st.session_state.current_doc_name)
        elif sources:
            st.session_state.current_doc_name = sources[0]
        
        st.session_state.current_doc_name = st.radio(
            "Primary Document", 
            sources, 
            index=current_doc_index,
            label_visibility="collapsed"
        )
    else:
        st.caption("No docs yet.")

    st.divider()

    # ── Quick stats ───────────────────────────────────────────────────────────
    stats = get_collection_stats()
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;gap:.35rem;'>
      <span class='badge'>📦 <b>{stats['total_chunks']}</b> chunks</span>
      <span class='badge'>📄 <b>{stats['total_documents']}</b> docs</span>
      <span class='badge'>💬 <b>{len(st.session_state.messages)}</b> messages</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages   = []
        st.session_state.session_id = None
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
chips_html = f"<span class='chip {chip_cls}'>{mode_cfg['emoji']} {mode}</span>"
if st.session_state.hybrid_mode:
    chips_html += "<span class='chip chip-teal'>🔀 Hybrid RAG</span>"
if st.session_state.voice_enabled:
    chips_html += "<span class='chip chip-orange'>🔊 Voice On</span>"

header_html = f"""
<div class='app-header'>
  <div style='display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:.5rem;'>
    <div>
      <h1>🧠 AI Learning Companion</h1>
      <p>Chat · Summarise · Quiz · Roadmap · Diagrams · Analytics · Voice</p>
    </div>
    <div style='display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.4rem;'>
      {chips_html}
    </div>
  </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "💬 Chat", "📤 Upload", "📋 Summary", "❓ Quiz",
    "🗺️ Roadmap", "🔀 Diagrams", "📊 Dashboard", "📁 History"
])
t_chat, t_upload, t_summary, t_quiz, t_roadmap, t_diagram, t_dash, t_history = tabs


# ══════════════════════════════════════════════════
# TAB 1: CHAT
# ══════════════════════════════════════════════════
with t_chat:
    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:.8rem;'>
          <span style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;'>Chat with your documents</span>
          <span class='chip {chip_cls}'>{mode_cfg["emoji"]} {mode}</span>
          {"<span class='chip chip-teal' style='font-size:.65rem;'>🔀 Hybrid</span>" if st.session_state.hybrid_mode else ""}
        </div>
        """, unsafe_allow_html=True)

        # Chat history
        chat_box = st.container(height=700)
        with chat_box:
            if not st.session_state.messages:
                st.markdown("""
                <div style='text-align:center;padding:2.5rem 1rem;color:#7c8499;'>
                  <div style='font-size:2.5rem;margin-bottom:.6rem;'>💬</div>
                  <p style='margin:0;'>No messages yet.<br>
                  <span style='font-size:.85rem;'>Upload a PDF and ask your first question!</span></p>
                </div>
                """, unsafe_allow_html=True)
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"]=="user" else "🧠"):
                    st.markdown(msg["content"])

        # Voice input option
        if st.session_state.voice_enabled:
            with st.expander("🎤 Voice Input", expanded=False):
                components.html(get_voice_input_html(), height=110)
                st.caption("After speaking, copy the transcript above and paste it in the chat input below.")

        # Text chat input
        user_input = st.chat_input(f"Ask anything... ({mode} mode active)")

        if user_input:
            st.session_state.question_log.append(user_input)
            st.session_state.messages.append({"role":"user","content":user_input})

            sid = ensure_session()
            save_message(sid, "user", user_input)

            with st.spinner(f"Thinking in {mode} mode..."):
                answer, _ = query_rag(
                    question=user_input,
                    top_k=5,
                    learning_mode=mode,
                    chat_history=st.session_state.messages[:-1],
                    username=user["username"],
                    expand_beyond_docs=st.session_state.hybrid_mode,
                    source_filters=st.session_state.active_sources,
                )

            st.session_state.messages.append({"role":"assistant","content":answer})
            save_message(sid, "assistant", answer)
            st.rerun()

        # TTS for last assistant message
        if st.session_state.voice_enabled and st.session_state.messages:
            last = st.session_state.messages[-1]
            if last["role"] == "assistant":
                with st.expander("🔊 Listen to last answer", expanded=False):
                    components.html(get_tts_html(last["content"], auto_play=False), height=55)

    with col_side:
        st.markdown('<p class="sec">💡 Tips</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("🎯","Be specific","Name the concept you want explained"),
            ("🔄","Follow up","Ask 'Can you give an example?'"),
            ("📊","Compare","Ask to compare two approaches"),
            ("🔬","Go deep","Switch to Research mode for analysis"),
        ]:
            st.markdown(f"""
            <div class='card card-a' style='padding:.75rem;'>
              <div style='font-size:1rem;'>{icon}</div>
              <div style='font-weight:600;font-size:.82rem;margin:3px 0;'>{title}</div>
              <div style='color:#7c8499;font-size:.73rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.question_log:
            st.markdown('<p class="sec" style="margin-top:.8rem;">🎯 Weak Topics</p>', unsafe_allow_html=True)
            if len(st.session_state.question_log) >= 3:
                if st.button("Analyse", use_container_width=True, key="quick_weak"):
                    with st.spinner("Analysing..."):
                        analysis = generate_weak_topic_analysis(st.session_state.question_log)
                    st.info(analysis[:500] + "...")
            else:
                st.caption(f"Ask {3-len(st.session_state.question_log)} more questions to unlock")


# ══════════════════════════════════════════════════
# TAB 2: UPLOAD
# ══════════════════════════════════════════════════
with t_upload:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.8rem;">📤 Upload Study Material</p>', unsafe_allow_html=True)
    col_up, col_right = st.columns([3,2])

    with col_up:
        uploaded_files = st.file_uploader("Drop PDFs", type=["pdf"], label_visibility="collapsed", accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                st.markdown(f"""
                <div class='card card-g'>
                  <div style='font-size:.75rem;color:#7c8499;'>Selected</div>
                  <div style='font-weight:600;margin-top:2px;'>📄 {uploaded_file.name}</div>
                  <div style='color:#7c8499;font-size:.75rem;'>{round(uploaded_file.size/1024,1)} KB</div>
                </div>""", unsafe_allow_html=True)

            if st.button("⚡ Process & Index All", use_container_width=True, type="primary"):
                total_files = len(uploaded_files)
                for i, uploaded_file in enumerate(uploaded_files):
                    prog_text = f"Processing file {i+1}/{total_files}: {uploaded_file.name}"
                    prog = st.progress(0, prog_text)
                    try:
                        upload_dir = get_user_upload_dir(user["username"])
                        fp         = os.path.join(upload_dir, uploaded_file.name)
                        with open(fp,"wb") as f:
                            f.write(uploaded_file.getbuffer())
                        prog.progress(25, f"({i+1}/{total_files}) Extracting text from {uploaded_file.name}...")
                        result = index_document(fp, source_name=uploaded_file.name)
                        prog.progress(85, f"({i+1}/{total_files}) Finalising {uploaded_file.name}...")
                        time.sleep(0.3); prog.progress(100, f"({i+1}/{total_files}) ✅ Done with {uploaded_file.name}!"); time.sleep(0.4)

                        if result["success"]:
                            st.success(f"✅ **{uploaded_file.name}** — {result['chunks']} chunks indexed.")
                            # Set the last uploaded doc as the current one
                            if i == total_files - 1:
                                st.session_state.current_doc_text = extract_text_from_pdf(fp)
                                st.session_state.current_doc_name = uploaded_file.name
                                st.session_state.session_id       = None  # fresh session
                        else:
                            st.error(f"❌ Error with {uploaded_file.name}: {result['error']}")
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")
                    finally:
                        prog.empty()

        # Study plan
        if st.session_state.current_doc_text:
            st.markdown('<p class="sec" style="margin-top:1.2rem;">📅 Study Plan</p>', unsafe_allow_html=True)
            days = st.slider("Days until exam/deadline", 1, 30, 7)
            if st.button("📅 Generate Study Plan", use_container_width=True):
                with st.spinner("Building your study plan..."):
                    st.session_state.study_plan_output = generate_study_plan(st.session_state.current_doc_text, days)
                    save_output(user["id"],"study_plan",f"Study Plan ({days} days)",
                                st.session_state.study_plan_output, st.session_state.current_doc_name)
            if st.session_state.study_plan_output:
                st.divider()
                st.markdown(st.session_state.study_plan_output)

    with col_right:
        st.markdown('<p class="sec">Indexed Documents</p>', unsafe_allow_html=True)
        vstats = get_collection_stats()
        if vstats["sources"]:
            for src in vstats["sources"]:
                active = src == st.session_state.current_doc_name
                st.markdown(f"""
                <div class='card' style='border-color:{"var(--accent)" if active else "var(--border)"};padding:.75rem;'>
                  <div style='font-size:.8rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>📄 {src}</div>
                  {"<div style='font-size:.68rem;color:var(--accent);margin-top:2px;'>● active</div>" if active else ""}
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='card card-a' style='padding:.8rem;'>
              <div style='font-size:.72rem;color:#7c8499;'>Total stored</div>
              <div style='font-size:1.5rem;font-weight:800;color:var(--accent);'>{vstats['total_chunks']}</div>
              <div style='font-size:.7rem;color:#7c8499;'>chunks · {vstats['total_documents']} docs</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("No docs indexed yet.")


# ══════════════════════════════════════════════════
# TAB 3: SUMMARY
# ══════════════════════════════════════════════════
with t_summary:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.6rem;">📋 Document Summarisation</p>', unsafe_allow_html=True)
    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first.")
    else:
        st.markdown(f"<div class='card card-a' style='padding:.65rem 1rem;font-size:.85rem;'>Active: <strong>📄 {st.session_state.current_doc_name}</strong></div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        if c1.button("📋 Chapter Summary",  use_container_width=True):
            with st.spinner("Summarising..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text,"chapter")
                save_output(user["id"],"summary","Chapter Summary",st.session_state.summary_output, st.session_state.current_doc_name)
        if c2.button("⚡ Quick Cheat Sheet", use_container_width=True):
            with st.spinner("Building cheat sheet..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text,"quick")
                save_output(user["id"],"summary","Quick Cheat Sheet",st.session_state.summary_output, st.session_state.current_doc_name)
        if c3.button("🌱 Simplify",          use_container_width=True):
            with st.spinner("Simplifying..."):
                st.session_state.summary_output = generate_summary(st.session_state.current_doc_text,"simplify")
                save_output(user["id"],"summary","Simplified Explanation",st.session_state.summary_output, st.session_state.current_doc_name)

        if st.session_state.summary_output:
            st.divider()
            st.markdown(st.session_state.summary_output)
            if st.session_state.voice_enabled:
                with st.expander("🔊 Listen to Summary"):
                    components.html(get_tts_html(st.session_state.summary_output, auto_play=False), height=55)
            st.download_button("⬇️ Download",data=st.session_state.summary_output,
                file_name=f"summary_{st.session_state.current_doc_name}.txt",use_container_width=True)


# ══════════════════════════════════════════════════
# TAB 4: QUIZ
# ══════════════════════════════════════════════════
with t_quiz:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.6rem;">❓ Quiz & Challenges</p>', unsafe_allow_html=True)

    if not st.session_state.current_doc_text:
        st.info("📤 Upload and process a PDF first.")
    else:
        quiz_tab1, quiz_tab2 = st.tabs(["📝 Quiz Generator", "🏆 Coding Challenge"])

        with quiz_tab1:
            num_q = st.slider("Questions", 3, 10, 5, key="quiz_n")
            c1,c2,c3 = st.columns(3)
            if c1.button("🔵 MCQ Quiz",      use_container_width=True):
                with st.spinner("Generating MCQs..."):
                    raw = generate_mcqs(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw,"mcq")
                    save_output(user["id"],"quiz","MCQ Quiz",st.session_state.quiz_output, st.session_state.current_doc_name)
            if c2.button("💼 Interview Qs",  use_container_width=True):
                with st.spinner("Generating..."):
                    raw = generate_interview_questions(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw,"interview")
                    save_output(user["id"],"quiz","Interview Questions",st.session_state.quiz_output, st.session_state.current_doc_name)
            if c3.button("📝 Short Answer",  use_container_width=True):
                with st.spinner("Generating..."):
                    raw = generate_short_answer_questions(st.session_state.current_doc_text, num_q)
                    st.session_state.quiz_output = format_quiz_for_display(raw,"short")
                    save_output(user["id"],"quiz","Short Answer Quiz",st.session_state.quiz_output, st.session_state.current_doc_name)

            if st.session_state.quiz_output:
                st.divider()
                st.markdown(st.session_state.quiz_output)
                st.download_button("⬇️ Download Quiz",data=st.session_state.quiz_output,
                    file_name=f"quiz_{st.session_state.current_doc_name}.txt",use_container_width=True)

        with quiz_tab2:
            st.markdown("Generate a coding challenge based on your study material topics.")
            ch_topic = st.text_input("Topic (or leave blank to auto-detect from document)", placeholder="e.g. recursion, sorting algorithms, neural networks")
            ch_diff  = st.select_slider("Difficulty", ["Beginner","Intermediate","Advanced"], value="Intermediate")
            ch_lang  = st.selectbox("Language", ["Python","JavaScript","Java","C++","Go","Rust"])
            if st.button("🏆 Generate Challenge", use_container_width=True, type="primary"):
                topic_used = ch_topic if ch_topic else st.session_state.current_doc_name.replace(".pdf","")
                with st.spinner("Generating coding challenge..."):
                    prompt = build_coding_challenge_prompt(topic_used, ch_diff.lower(), ch_lang)
                    st.session_state.challenge_output = ask_llm(prompt)
                    save_output(user["id"],"quiz",f"Coding Challenge: {topic_used}",
                                st.session_state.challenge_output, st.session_state.current_doc_name)
            if st.session_state.challenge_output:
                st.divider()
                st.markdown(st.session_state.challenge_output)


# ══════════════════════════════════════════════════
# TAB 5: ROADMAP
# ══════════════════════════════════════════════════
with t_roadmap:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.6rem;">🗺️ Learning Roadmap Generator</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499;font-size:.85rem;margin-bottom:1rem;">Tell the AI your learning goal — it will generate a personalised, phase-by-phase roadmap.</p>', unsafe_allow_html=True)

    rm_col1, rm_col2 = st.columns([2,1])
    with rm_col1:
        goal   = st.text_area("What do you want to learn or achieve?",
            placeholder="e.g. 'Become an AI/ML Engineer', 'Master React.js', 'Learn Data Science from scratch'",
            height=80)
    with rm_col2:
        level  = st.selectbox("Current Level", ["complete beginner","beginner","intermediate","advanced"])
        weeks  = st.slider("Weeks available", 4, 52, 12)

    if st.button("🗺️ Generate My Roadmap", use_container_width=True, type="primary", disabled=not goal):
        with st.spinner("Designing your personalised learning roadmap..."):
            roadmap_text = generate_roadmap(goal, level, weeks)
            st.session_state.roadmap_output = roadmap_text
            from utils.roadmap import parse_roadmap_phases
            phases = parse_roadmap_phases(roadmap_text)
            st.session_state.roadmap_phases = phases
            rm_id = save_roadmap(user["id"], goal, level, weeks, roadmap_text)
            st.session_state.roadmap_id = rm_id
            save_output(user["id"],"roadmap",f"Roadmap: {goal[:50]}",roadmap_text)

    # Show existing roadmap if we have one
    if not st.session_state.roadmap_output:
        existing = load_latest_roadmap(user["id"])
        if existing:
            st.session_state.roadmap_output = existing["content"]
            st.session_state.roadmap_phases  = existing["phases"]
            st.session_state.roadmap_id      = existing["id"]

    if st.session_state.roadmap_output:
        st.divider()
        rd_main, rd_prog = st.columns([3,1])

        with rd_main:
            st.markdown(st.session_state.roadmap_output)
            st.download_button("⬇️ Download Roadmap", data=st.session_state.roadmap_output,
                file_name="learning_roadmap.md", use_container_width=True)

        with rd_prog:
            if st.session_state.roadmap_phases and st.session_state.roadmap_id:
                st.markdown('<p class="sec">✅ Progress Tracker</p>', unsafe_allow_html=True)
                rm_id    = st.session_state.roadmap_id
                progress = get_progress(user["id"], rm_id)
                pct      = get_completion_percentage(user["id"], rm_id, st.session_state.roadmap_phases)

                # Progress bar
                st.markdown(f"""
                <div style='margin-bottom:.8rem;'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                    <span style='font-size:.78rem;color:#7c8499;'>Overall Progress</span>
                    <span style='font-size:.78rem;font-weight:700;color:var(--accent);'>{pct}%</span>
                  </div>
                  <div style='background:#1e2333;border-radius:4px;height:8px;'>
                    <div style='background:linear-gradient(90deg,#6c63ff,#00d4aa);height:8px;border-radius:4px;width:{pct}%;transition:width .3s;'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                for phase_data in st.session_state.roadmap_phases[:3]:  # show first 3 phases
                    phase_name = phase_data["phase"]
                    completed  = progress.get(phase_name, [])
                    with st.expander(f"📍 {phase_name[:35]}...", expanded=False):
                        for topic in phase_data["topics"]:
                            done = topic in completed
                            if st.checkbox(topic[:45], value=done, key=f"rm_{rm_id}_{phase_name}_{topic}"):
                                if not done:
                                    mark_topic_complete(user["id"], rm_id, phase_name, topic)
                                    st.rerun()


# ══════════════════════════════════════════════════
# TAB 6: DIAGRAMS
# ══════════════════════════════════════════════════
with t_diagram:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.6rem;">🔀 Visual Diagram Generator</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7c8499;font-size:.85rem;margin-bottom:1rem;">Generate Mermaid diagrams for any concept — rendered live in your browser.</p>', unsafe_allow_html=True)

    dg_col1, dg_col2 = st.columns([3,1])
    with dg_col1:
        dg_topic = st.text_input("Concept or topic to visualise",
            placeholder="e.g. 'How neural networks learn', 'Git workflow', 'HTTP request lifecycle'")
    with dg_col2:
        dg_type_label = st.selectbox("Diagram Type",
            [v["label"] for v in DIAGRAM_TYPES.values()], label_visibility="visible")
        dg_type = [k for k,v in DIAGRAM_TYPES.items() if v["label"]==dg_type_label][0]

    if st.button("🎨 Generate Diagram", use_container_width=True, type="primary", disabled=not dg_topic):
        with st.spinner("Generating diagram..."):
            code, err = generate_diagram(dg_topic, dg_type)
        if err:
            st.error(f"❌ {err}")
        else:
            st.session_state.diagram_code = code
            save_output(user["id"],"diagram",f"Diagram: {dg_topic[:40]}",code)

    if st.session_state.diagram_code:
        st.divider()
        diag_render, diag_code = st.columns([3,2])

        with diag_render:
            st.markdown("**Rendered Diagram**")
            html_out = mermaid_to_html(st.session_state.diagram_code)
            components.html(html_out, height=600, scrolling=False)
            st.caption("🖱️ Drag to pan, use your mouse wheel to zoom.")

        with diag_code:
            st.markdown("**Mermaid Source**")
            st.code(st.session_state.diagram_code, language="text")
            st.download_button("⬇️ Download .mmd", data=st.session_state.diagram_code,
                file_name=f"diagram_{dg_topic[:20]}.mmd", use_container_width=True)


# ══════════════════════════════════════════════════
# TAB 7: DASHBOARD
# ══════════════════════════════════════════════════
with t_dash:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.8rem;">📊 Learning Analytics</p>', unsafe_allow_html=True)

    data = get_dashboard_data(user["id"])
    stats_d  = data["stats"]
    streak_d = data["streak"]
    topics_d = data["topics"]
    modes_d  = data["modes"]

    # ── Key metrics ───────────────────────────────────────────────────────────
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    metrics = [
        (m1, "💬", stats_d["total_messages"], "Questions Asked"),
        (m2, "📄", stats_d["docs_studied"],   "Docs Studied"),
        (m3, "🗓️", stats_d["days_active"],    "Days Active"),
        (m4, "🔥", streak_d["current"],        "Day Streak"),
        (m5, "📦", stats_d["outputs_saved"],   "Items Saved"),
        (m6, "❓", stats_d["quizzes_taken"],   "Quizzes Taken"),
    ]
    for col, icon, val, label in metrics:
        col.markdown(f"""
        <div class='stat-card'>
          <div style='font-size:1.2rem;'>{icon}</div>
          <div class='num' style='color:var(--accent);'>{val}</div>
          <div class='lbl'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Top topics + Mode distribution ───────────────────────────────────────
    col_topics, col_modes, col_streak = st.columns([2,1,1])

    with col_topics:
        st.markdown('<p class="sec">🔥 Most Studied Topics</p>', unsafe_allow_html=True)
        if topics_d:
            max_count = topics_d[0]["count"] if topics_d else 1
            for t in topics_d[:8]:
                pct = int((t["count"]/max_count)*100)
                st.markdown(f"""
                <div style='margin-bottom:.5rem;'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:2px;'>
                    <span style='font-size:.82rem;'>{t["topic"]}</span>
                    <span style='font-size:.75rem;color:#7c8499;'>{t["count"]}x</span>
                  </div>
                  <div style='background:#1e2333;border-radius:3px;height:5px;'>
                    <div style='background:var(--accent);height:5px;border-radius:3px;width:{pct}%;'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Ask more questions to see topic trends.")

    with col_modes:
        st.markdown('<p class="sec">🎓 Mode Usage</p>', unsafe_allow_html=True)
        mode_colors = {"Beginner":"var(--green)","Exam":"var(--accent)","Practical":"var(--orange)","Interview":"var(--teal)","Research":"var(--teal)","Roadmap":"var(--yellow)"}
        total_mode = sum(modes_d.values()) or 1
        for m_name, m_count in modes_d.items():
            pct = int((m_count/total_mode)*100)
            clr = mode_colors.get(m_name, "var(--muted)")
            st.markdown(f"""
            <div style='margin-bottom:.5rem;'>
              <div style='display:flex;justify-content:space-between;margin-bottom:2px;'>
                <span style='font-size:.8rem;'>{LEARNING_MODES.get(m_name,{}).get("emoji","📚")} {m_name}</span>
                <span style='font-size:.73rem;color:#7c8499;'>{pct}%</span>
              </div>
              <div style='background:#1e2333;border-radius:3px;height:5px;'>
                <div style='background:{clr};height:5px;border-radius:3px;width:{pct}%;'></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with col_streak:
        st.markdown('<p class="sec">🔥 Study Streak</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card card-y' style='text-align:center;'>
          <div style='font-size:2.5rem;'>🔥</div>
          <div style='font-size:2rem;font-weight:800;color:var(--yellow);'>{streak_d["current"]}</div>
          <div style='font-size:.75rem;color:#7c8499;'>day streak</div>
        </div>
        <div class='card card-a' style='text-align:center;margin-top:.5rem;'>
          <div style='font-size:.72rem;color:#7c8499;'>Longest streak</div>
          <div style='font-size:1.5rem;font-weight:800;color:var(--accent);'>{streak_d["longest"]}</div>
          <div style='font-size:.7rem;color:#7c8499;'>days</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Project recommendations ───────────────────────────────────────────────
    if st.session_state.current_doc_text:
        st.divider()
        st.markdown('<p class="sec">🚀 Project Recommendations</p>', unsafe_allow_html=True)
        if st.button("Generate Project Ideas from Current Document", use_container_width=True):
            with st.spinner("Brainstorming projects..."):
                st.session_state.project_output = generate_project_recommendations(st.session_state.current_doc_text)
                save_output(user["id"],"project","Project Ideas",st.session_state.project_output, st.session_state.current_doc_name)
        if st.session_state.project_output:
            st.markdown(st.session_state.project_output)

    # ── Weak topic analysis ───────────────────────────────────────────────────
    q_log = st.session_state.question_log
    if len(q_log) >= 3:
        st.divider()
        st.markdown('<p class="sec">🎯 Weak Topic Analysis</p>', unsafe_allow_html=True)
        if st.button("🎯 Analyse My Weak Areas", use_container_width=True):
            with st.spinner("Analysing question patterns..."):
                analysis = generate_weak_topic_analysis(q_log)
            st.markdown(analysis)


# ══════════════════════════════════════════════════
# TAB 8: HISTORY
# ══════════════════════════════════════════════════
with t_history:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;margin-bottom:.6rem;">📁 Session History & Saved Outputs</p>', unsafe_allow_html=True)

    hist_tab1, hist_tab2 = st.tabs(["💬 Chat Sessions", "📦 Saved Outputs"])

    with hist_tab1:
        sessions = list_sessions(user["id"], limit=15)
        if not sessions:
            st.info("No chat sessions yet. Start a conversation in the Chat tab.")
        else:
            for sesh in sessions:
                with st.expander(f"💬 {sesh['doc_name'] or 'General'} · {sesh['learning_mode']} · {sesh['created_at'][:10]} · {sesh['message_count']} msgs"):
                    col_load, col_del = st.columns([3,1])
                    if col_load.button("📂 Load Session", key=f"load_{sesh['id']}"):
                        msgs = load_messages(sesh["id"])
                        st.session_state.messages   = msgs
                        st.session_state.session_id = sesh["id"]
                        st.session_state.learning_mode = sesh["learning_mode"]
                        st.success(f"✅ Loaded session with {len(msgs)} messages. Switch to Chat tab.")
                    if col_del.button("🗑️", key=f"del_s_{sesh['id']}", help="Delete session"):
                        delete_session(sesh["id"], user["id"])
                        st.rerun()

                    # Preview first 3 messages
                    msgs_preview = load_messages(sesh["id"])[:4]
                    for msg in msgs_preview:
                        st.markdown(f"**{'You' if msg['role']=='user' else '🧠 AI'}**: {msg['content'][:150]}...")

    with hist_tab2:
        output_types = {"All": None,"Quizzes":"quiz","Summaries":"summary","Roadmaps":"roadmap","Diagrams":"diagram","Projects":"project","Study Plans":"study_plan"}
        filter_label = st.selectbox("Filter by type", list(output_types.keys()))
        filter_type  = output_types[filter_label]

        outputs = load_saved_outputs(user["id"], filter_type)
        if not outputs:
            st.info("No saved outputs yet. Generate quizzes, summaries, or roadmaps to save them here.")
        else:
            for out in outputs:
                icon = {"quiz":"❓","summary":"📋","roadmap":"🗺️","diagram":"🔀","project":"🚀","study_plan":"📅"}.get(out["output_type"],"📄")
                with st.expander(f"{icon} {out['title']} · {out['created_at'][:10]}"):
                    st.markdown(out["content"][:1000] + ("..." if len(out["content"])>1000 else ""))
                    st.download_button("⬇️ Download", data=out["content"],
                        file_name=f"{out['output_type']}_{out['id']}.txt",
                        key=f"dl_out_{out['id']}")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1rem 0;color:#252a3a;font-size:.72rem;'>
  AI Learning Companion v3 · Streamlit · ChromaDB · sentence-transformers · Web Speech API
</div>
""", unsafe_allow_html=True)