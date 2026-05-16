"""
Auth Manager
=============
WHY SQLite and not a cloud service:
- Zero extra dependencies for a portfolio/Streamlit Cloud deploy.
- Works offline, no signup required for your own app.
- Easy to swap to PostgreSQL/Supabase later — just change _get_db().

Security choices:
- Passwords hashed with bcrypt (industry standard, never stored in plain text).
- Sessions stored in st.session_state (Streamlit's built-in, server-side).
- Each user gets an isolated data namespace so PDFs and chat history
  never leak between accounts.

The auth flow:
  signup()  -> hash password -> store user -> return success
  login()   -> fetch user -> verify hash -> set session -> return user_id
  logout()  -> clear session state
  is_authenticated() -> check session state (call on every page)
"""

import sqlite3
import os
import hashlib
import secrets
from typing import Optional, Tuple
from datetime import datetime

import streamlit as st

DB_PATH = "data/users.db"


# ────────────────────────────────────────────────────────────────────────────
# DB SETUP
# ────────────────────────────────────────────────────────────────────────────
def _get_db() -> sqlite3.Connection:
    """Return a SQLite connection. Creates DB file if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db() -> None:
    """
    Create the users table if it doesn't already exist.
    Call once at app startup.
    """
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            email      TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────────────────────
# PASSWORD HASHING (bcrypt preferred; falls back to sha256 if bcrypt absent)
# ────────────────────────────────────────────────────────────────────────────
def _hash_password(plain: str) -> str:
    try:
        import bcrypt
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        # Fallback: sha256 with a random salt (good enough for portfolio use)
        salt   = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + plain).encode()).hexdigest()
        return f"sha256${salt}${hashed}"


def _verify_password(plain: str, stored: str) -> bool:
    try:
        import bcrypt
        return bcrypt.checkpw(plain.encode(), stored.encode())
    except ImportError:
        if stored.startswith("sha256$"):
            _, salt, hashed = stored.split("$", 2)
            return hashlib.sha256((salt + plain).encode()).hexdigest() == hashed
        return False


# ────────────────────────────────────────────────────────────────────────────
# PUBLIC AUTH FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────
def signup(username: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user.

    Returns:
        (True, "success message") or (False, "error message")
    """
    username = username.strip().lower()
    email    = email.strip().lower()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email:
        return False, "Please enter a valid email address."

    hashed = _hash_password(password)
    conn   = _get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?,?,?,?)",
            (username, email, hashed, datetime.utcnow().isoformat())
        )
        conn.commit()
        return True, f"Account created! Welcome, {username} 🎉"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken. Please choose another."
        if "email" in str(e):
            return False, "An account with this email already exists."
        return False, "Signup failed. Please try again."
    finally:
        conn.close()


def login(username: str, password: str) -> Tuple[bool, str]:
    """
    Verify credentials and set Streamlit session state.

    Returns:
        (True, "welcome message") or (False, "error message")
    """
    username = username.strip().lower()
    conn     = _get_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return False, "Username not found. Please check or sign up."

    if not _verify_password(password, row["password"]):
        return False, "Incorrect password. Please try again."

    # Set session
    st.session_state.authenticated = True
    st.session_state.user_id       = row["id"]
    st.session_state.username      = row["username"]
    st.session_state.email         = row["email"]

    return True, f"Welcome back, {row['username']}! 👋"


def logout() -> None:
    """Clear auth session and reset all user-specific state."""
    for key in ["authenticated", "user_id", "username", "email",
                "messages", "pdf_path", "pdf_processed",
                "current_doc_text", "current_doc_name",
                "uploaded_docs", "question_log",
                "quiz_output", "summary_output", "project_output"]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    """Check if the current Streamlit session has a logged-in user."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[dict]:
    """Return current user info dict, or None if not logged in."""
    if not is_authenticated():
        return None
    return {
        "id":       st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "email":    st.session_state.get("email"),
    }


def get_user_upload_dir(username: str) -> str:
    """
    Return a user-specific upload directory path.
    This isolates each user's PDFs from other users.
    """
    path = os.path.join("data", "uploaded_pdfs", username)
    os.makedirs(path, exist_ok=True)
    return path
