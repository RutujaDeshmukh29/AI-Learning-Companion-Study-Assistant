"""
Roadmap Generator Module
=========================
WHY this is a differentiating feature:
Most AI study tools only answer questions. This module makes the app
proactive — it generates a full learning path BEFORE the user even
asks their first question. That's the "AI mentor" experience.

Architecture:
- generate_roadmap()     -> calls LLM with build_roadmap_prompt()
- parse_roadmap_phases() -> extracts phases for progress tracking
- save_roadmap()         -> persists to SQLite for session continuity
- load_roadmap()         -> restores roadmap on next login

The roadmap is stored per-user so each user has their own learning path.
"""

import sqlite3
import os
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from utils.llm     import ask_llm
from utils.prompts import build_roadmap_prompt, build_study_plan_prompt

DB_PATH = "data/users.db"


# ────────────────────────────────────────────────────────────────────────────
# DB SETUP
# ────────────────────────────────────────────────────────────────────────────
def init_roadmap_table() -> None:
    """Create roadmaps table if it doesn't exist. Called at app startup."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            goal       TEXT    NOT NULL,
            level      TEXT    NOT NULL,
            weeks      INTEGER NOT NULL,
            content    TEXT    NOT NULL,
            phases     TEXT    NOT NULL,
            created_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_progress (
            user_id    INTEGER NOT NULL,
            roadmap_id INTEGER NOT NULL,
            phase      TEXT    NOT NULL,
            topic      TEXT    NOT NULL,
            completed  INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, roadmap_id, phase, topic),
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id)
        )
    """)
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────────────────────────────────
# GENERATION
# ────────────────────────────────────────────────────────────────────────────
def generate_roadmap(
    goal: str,
    current_level: str = "beginner",
    weeks_available: int = 12,
) -> str:
    """
    Generate a personalised learning roadmap using the LLM.

    Args:
        goal:            What the user wants to achieve (e.g. "become an ML engineer")
        current_level:   beginner / intermediate / advanced
        weeks_available: How many weeks they have

    Returns:
        Formatted markdown roadmap string.
    """
    prompt = build_roadmap_prompt(goal, current_level, weeks_available)
    return ask_llm(prompt)


def generate_study_plan(doc_text: str, days: int = 7) -> str:
    """Generate a day-by-day study plan from uploaded document content."""
    prompt = build_study_plan_prompt(doc_text, exam_date_days=days)
    return ask_llm(prompt)


# ────────────────────────────────────────────────────────────────────────────
# PARSING  — extract structured phases from the markdown roadmap
# ────────────────────────────────────────────────────────────────────────────
def parse_roadmap_phases(roadmap_text: str) -> List[Dict[str, Any]]:
    """
    Extract phase names and their checkbox topics from the roadmap markdown.
    Used for the progress tracker UI.

    Returns:
        [{"phase": "Phase 1: Foundation", "topics": ["Topic A", "Topic B"]}, ...]
    """
    phases = []
    current_phase = None
    topics = []

    for line in roadmap_text.split("\n"):
        line = line.strip()

        # Detect phase headers like "## Phase 1: Foundation"
        phase_match = re.match(r"^#{1,3}\s+(Phase\s+\d+[:\s].+)", line, re.IGNORECASE)
        if phase_match:
            if current_phase and topics:
                phases.append({"phase": current_phase, "topics": topics})
            current_phase = phase_match.group(1).strip()
            topics = []
            continue

        # Detect checkbox items like "- [ ] Topic name"
        topic_match = re.match(r"^[-*]\s+\[[ x]\]\s+(.+)", line)
        if topic_match and current_phase:
            topics.append(topic_match.group(1).strip())

    if current_phase and topics:
        phases.append({"phase": current_phase, "topics": topics})

    return phases


# ────────────────────────────────────────────────────────────────────────────
# PERSISTENCE
# ────────────────────────────────────────────────────────────────────────────
def save_roadmap(
    user_id: int,
    goal: str,
    level: str,
    weeks: int,
    content: str,
) -> int:
    """
    Save a generated roadmap to DB and return its ID.
    """
    phases = parse_roadmap_phases(content)
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """INSERT INTO roadmaps (user_id, goal, level, weeks, content, phases, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, goal, level, weeks, content, json.dumps(phases), datetime.utcnow().isoformat())
    )
    roadmap_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return roadmap_id


def load_latest_roadmap(user_id: int) -> Optional[Dict[str, Any]]:
    """Load the most recent roadmap for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row  = conn.execute(
        "SELECT * FROM roadmaps WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id":      row["id"],
        "goal":    row["goal"],
        "level":   row["level"],
        "weeks":   row["weeks"],
        "content": row["content"],
        "phases":  json.loads(row["phases"]),
        "created": row["created_at"],
    }


def load_all_roadmaps(user_id: int) -> List[Dict]:
    """Load all roadmaps for a user (for history view)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, goal, level, weeks, created_at FROM roadmaps WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# PROGRESS TRACKING
# ────────────────────────────────────────────────────────────────────────────
def mark_topic_complete(user_id: int, roadmap_id: int, phase: str, topic: str) -> None:
    """Mark a roadmap topic as completed."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO roadmap_progress (user_id, roadmap_id, phase, topic, completed)
           VALUES (?, ?, ?, ?, 1)""",
        (user_id, roadmap_id, phase, topic)
    )
    conn.commit()
    conn.close()


def get_progress(user_id: int, roadmap_id: int) -> Dict[str, List[str]]:
    """
    Get completed topics for a roadmap.
    Returns: {"Phase 1: Foundation": ["Topic A", "Topic B"], ...}
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT phase, topic FROM roadmap_progress WHERE user_id=? AND roadmap_id=? AND completed=1",
        (user_id, roadmap_id)
    ).fetchall()
    conn.close()

    progress: Dict[str, List[str]] = {}
    for phase, topic in rows:
        progress.setdefault(phase, []).append(topic)
    return progress


def get_completion_percentage(user_id: int, roadmap_id: int, phases: List[Dict]) -> float:
    """Calculate overall roadmap completion percentage."""
    total     = sum(len(p["topics"]) for p in phases)
    if total == 0:
        return 0.0
    progress  = get_progress(user_id, roadmap_id)
    completed = sum(len(v) for v in progress.values())
    return round((completed / total) * 100, 1)