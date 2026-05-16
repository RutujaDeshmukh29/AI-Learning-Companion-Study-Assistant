import streamlit as st
import os
from utils.rag_pipeline import run_rag_pipeline

# --- Constants ---
PDF_UPLOADS_DIR = "data/uploaded_pdfs"

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="AI Learning Companion",
    page_icon="📘",
    layout="wide"
)

# --- App Title ---
st.title("📘 AI Learning Companion")
st.write("Your personal AI-powered study assistant.")

# --- Session State Initialization ---
def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False

initialize_session_state()

# --- Helper Functions ---
def process_pdf(uploaded_file):
    """Process the uploaded PDF file."""
    os.makedirs(PDF_UPLOADS_DIR, exist_ok=True)
    pdf_path = os.path.join(PDF_UPLOADS_DIR, uploaded_file.name)
    
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.pdf_path = pdf_path
    st.session_state.pdf_processed = True
    st.success("PDF uploaded and processed successfully!")

def new_chat():
    """Reset the chat history."""
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]


# --- Sidebar ---
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file:
        if st.session_state.pdf_path != os.path.join(PDF_UPLOADS_DIR, uploaded_file.name):
            process_pdf(uploaded_file)
            
    if st.button("New Chat"):
        new_chat()

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Main Logic ---
if prompt := st.chat_input("Ask a question about your PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.pdf_processed:
        with st.chat_message("assistant"):
            st.warning("Please upload a PDF file first.")
        st.stop()

    with st.spinner("Thinking..."):
        answer, retrieved_chunks = run_rag_pipeline(st.session_state.pdf_path, prompt)
        
    with st.chat_message("assistant"):
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.expander("View Retrieved Context"):
            for i, chunk in enumerate(retrieved_chunks):
                st.markdown(f"""
> **Chunk {i+1}**
---
{chunk}
""")
