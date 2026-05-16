"""
Chat History Module
====================
WHY persistent history matters:
Without this, every Streamlit rerun wipes the conversation.
Users can't review what they learned, revisit answers, or continue
a session after closing the browser. This module fixes that.

Design:
- SQLite stores all chat messages per user per session.
- A "session" is one study session (one uploaded doc + conversation).
- Users can load any past session and continue from where they left off.
- The analytics module reads history to calculate study stats.

Tables:
  chat_sessions  — metadata (user, doc name, timestamp)
  chat_messages  — individual messages linked to a session
  saved_outputs  — quizzes, summaries, roadmaps the user saved
"""

import sqlite3
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

DB_PATH = "data/users.db"


# ────────────────────────────────────────────────────────────────────────────
# DB SETUP
# ────────────────────────────────────────────────────────────────────────────
def init_history_tables() -> None:
    """Create history tables. Called once at startup."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            doc_name     TEXT    DEFAULT '',
            learning_mode TEXT   DEFAULT 'Beginner',
            created_at   TEXT    NOT NULL,
            updated_at   TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            created_at TEXT    NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        );

        CREATE TABLE IF NOT EXISTS saved_outputs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            output_type TEXT   NOT NULL,
            title      TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            doc_name   TEXT    DEFAULT '',
            created_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────────────────────
# SESSION MANAGEMENT
# ────────────────────────────────────────────────────────────────────────────
def create_session(user_id: int, doc_name: str = "", mode: str = "Beginner") -> int:
    """Create a new chat session. Returns the session ID."""
    now  = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute(
        "INSERT INTO chat_sessions (user_id, doc_name, learning_mode, created_at, updated_at) VALUES (?,?,?,?,?)",
        (user_id, doc_name, mode, now, now)
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_or_create_session(user_id: int, doc_name: str, mode: str) -> int:
    """
    Get today's active session for this doc, or create a new one.
    This prevents creating a new session on every rerun.
    """
    today = datetime.utcnow().date().isoformat()
    conn  = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """SELECT id FROM chat_sessions
           WHERE user_id=? AND doc_name=? AND created_at LIKE ?
           ORDER BY id DESC LIMIT 1""",
        (user_id, doc_name, f"{today}%")
    ).fetchone()
    conn.close()

    if row:
        return row["id"]
    return create_session(user_id, doc_name, mode)


def list_sessions(user_id: int, limit: int = 10) -> List[Dict]:
    """List recent chat sessions for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT s.id, s.doc_name, s.learning_mode, s.created_at,
                  COUNT(m.id) as message_count
           FROM chat_sessions s
           LEFT JOIN chat_messages m ON m.session_id = s.id
           WHERE s.user_id = ?
           GROUP BY s.id
           ORDER BY s.id DESC LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# MESSAGE MANAGEMENT
# ────────────────────────────────────────────────────────────────────────────
def save_message(session_id: int, role: str, content: str) -> None:
    """Save a single chat message to a session."""
    conn = sqlite3.connect(DB_PATH)
    now  = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
        (session_id, role, content, now)
    )
    conn.execute(
        "UPDATE chat_sessions SET updated_at=? WHERE id=?",
        (now, session_id)
    )
    conn.commit()
    conn.close()


def save_messages_batch(session_id: int, messages: List[Dict]) -> None:
    """Save multiple messages at once (used when switching sessions)."""
    now  = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.executemany(
        "INSERT OR IGNORE INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
        [(session_id, m["role"], m["content"], now) for m in messages]
    )
    conn.execute("UPDATE chat_sessions SET updated_at=? WHERE id=?", (now, session_id))
    conn.commit()
    conn.close()


def load_messages(session_id: int) -> List[Dict]:
    """Load all messages for a session, ordered by time."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT role, content FROM chat_messages WHERE session_id=? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def delete_session(session_id: int, user_id: int) -> bool:
    """Delete a session and all its messages (ownership verified)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM chat_messages WHERE session_id IN "
        "(SELECT id FROM chat_sessions WHERE id=? AND user_id=?)",
        (session_id, user_id)
    )
    conn.execute(
        "DELETE FROM chat_sessions WHERE id=? AND user_id=?",
        (session_id, user_id)
    )
    conn.commit()
    conn.close()
    return True


# ────────────────────────────────────────────────────────────────────────────
# SAVED OUTPUTS (quizzes, summaries, roadmaps)
# ────────────────────────────────────────────────────────────────────────────
def save_output(user_id: int, output_type: str, title: str, content: str, doc_name: str = "") -> int:
    """
    Save a generated AI output (quiz, summary, roadmap) for later access.
    output_type: "quiz" | "summary" | "roadmap" | "study_plan" | "diagram"
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute(
        "INSERT INTO saved_outputs (user_id, output_type, title, content, doc_name, created_at) VALUES (?,?,?,?,?,?)",
        (user_id, output_type, title, content, doc_name, datetime.utcnow().isoformat())
    )
    out_id = cur.lastrowid
    conn.commit()
    conn.close()
    return out_id


def load_saved_outputs(user_id: int, output_type: str = None, limit: int = 20) -> List[Dict]:
    """Load saved outputs, optionally filtered by type."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if output_type:
        rows = conn.execute(
            "SELECT * FROM saved_outputs WHERE user_id=? AND output_type=? ORDER BY id DESC LIMIT ?",
            (user_id, output_type, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM saved_outputs WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_output(output_id: int, user_id: int) -> None:
    """Delete a saved output (ownership verified)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM saved_outputs WHERE id=? AND user_id=?", (output_id, user_id))
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────────────────────
# ANALYTICS HELPERS
# ────────────────────────────────────────────────────────────────────────────
def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    Aggregate stats for the analytics dashboard.
    Returns total sessions, messages, docs studied, and outputs saved.
    """
    conn = sqlite3.connect(DB_PATH)
    stats = {}

    stats["total_sessions"] = conn.execute(
        "SELECT COUNT(*) FROM chat_sessions WHERE user_id=?", (user_id,)
    ).fetchone()[0]

    stats["total_messages"] = conn.execute(
        "SELECT COUNT(*) FROM chat_messages m "
        "JOIN chat_sessions s ON s.id = m.session_id "
        "WHERE s.user_id=? AND m.role='user'", (user_id,)
    ).fetchone()[0]

    stats["docs_studied"] = conn.execute(
        "SELECT COUNT(DISTINCT doc_name) FROM chat_sessions WHERE user_id=? AND doc_name!=''",
        (user_id,)
    ).fetchone()[0]

    stats["outputs_saved"] = conn.execute(
        "SELECT COUNT(*) FROM saved_outputs WHERE user_id=?", (user_id,)
    ).fetchone()[0]

    stats["quizzes_taken"] = conn.execute(
        "SELECT COUNT(*) FROM saved_outputs WHERE user_id=? AND output_type='quiz'",
        (user_id,)
    ).fetchone()[0]

    # Days active (distinct study days)
    stats["days_active"] = conn.execute(
        "SELECT COUNT(DISTINCT DATE(created_at)) FROM chat_sessions WHERE user_id=?",
        (user_id,)
    ).fetchone()[0]

    conn.close()
    return stats