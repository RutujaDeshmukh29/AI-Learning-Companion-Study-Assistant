"""
Auth UI Module
===============
Renders the Login and Signup screens inside Streamlit.
Kept separate from app.py so app.py stays clean and focused on features.

Design decision:
- Single page with tab switching (Login | Sign Up) rather than separate pages.
- Clean card-style centered layout that matches the dark theme.
- Inline validation feedback (no page reload needed for errors).
"""

import streamlit as st
from auth.auth_manager import login, signup, init_db


def show_auth_page() -> None:
    """
    Render the full authentication page.
    Call this in app.py when is_authenticated() returns False.
    Returns (implicitly) when the user successfully logs in by setting session state.
    """
    init_db()   # ensure DB exists (idempotent)

    # ── centered card layout ────────────────────────────────────────────────
    _, col, _ = st.columns([1, 2, 1])

    with col:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
          <div style="font-size:3rem;">🧠</div>
          <h1 style="font-family:'Syne',sans-serif; font-size:1.8rem;
                     font-weight:800; margin:0.5rem 0 0.2rem;">
            AI Learning Companion
          </h1>
          <p style="color:#7c8499; font-size:0.9rem; margin:0;">
            Your personal AI-powered study assistant
          </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔐 Login", "✨ Sign Up"])

        # ── LOGIN ────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="your_username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login →", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please fill in both fields.")
                else:
                    ok, msg = login(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("""
            <p style="text-align:center; color:#7c8499; font-size:0.8rem; margin-top:1rem;">
              Don't have an account? Switch to the Sign Up tab above.
            </p>
            """, unsafe_allow_html=True)

        # ── SIGN UP ──────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=True):
                new_username = st.text_input("Username", placeholder="choose_a_username")
                new_email    = st.text_input("Email",    placeholder="you@example.com")
                new_password = st.text_input("Password", type="password", placeholder="min 6 characters")
                confirm_pw   = st.text_input("Confirm Password", type="password", placeholder="repeat password")
                submitted_s  = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

            if submitted_s:
                if not all([new_username, new_email, new_password, confirm_pw]):
                    st.error("Please fill in all fields.")
                elif new_password != confirm_pw:
                    st.error("Passwords don't match.")
                else:
                    ok, msg = signup(new_username, new_email, new_password)
                    if ok:
                        st.success(msg + " Please switch to the Login tab.")
                    else:
                        st.error(msg)

        # ── demo hint ────────────────────────────────────────────────────────
        st.markdown("""
        <div style="background:#13161e; border:1px solid #252a3a; border-radius:10px;
                    padding:0.9rem 1.2rem; margin-top:1.5rem; font-size:0.82rem; color:#7c8499;">
          <strong style="color:#6c63ff;">New here?</strong>
          Sign up with any username and password to get started.
          Your uploads and chat history are private to your account.
        </div>
        """, unsafe_allow_html=True)
