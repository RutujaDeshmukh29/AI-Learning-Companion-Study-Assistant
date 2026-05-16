"""
Analytics Module
=================
WHY a learning analytics dashboard matters:
This is what turns the app from a "chatbot" into a "learning platform."
Users can see their progress, study streaks, most-studied topics, and
areas that need more attention. It's also great for the portfolio demo.

This module reads from the history tables (no extra AI calls needed).
All computation is local — fast and free.
"""

import sqlite3
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import Counter
import re

DB_PATH = "data/users.db"


# ────────────────────────────────────────────────────────────────────────────
# STUDY STREAK
# ────────────────────────────────────────────────────────────────────────────
def get_study_streak(user_id: int) -> Dict[str, int]:
    """
    Calculate current and longest study streaks.
    A "study day" = any day with at least one chat message.

    Returns:
        {"current": 5, "longest": 12, "total_days": 18}
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT DISTINCT DATE(m.created_at) as study_date
           FROM chat_messages m
           JOIN chat_sessions s ON s.id = m.session_id
           WHERE s.user_id = ?
           ORDER BY study_date DESC""",
        (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return {"current": 0, "longest": 0, "total_days": 0}

    dates = [datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows]
    today = datetime.utcnow().date()

    # Current streak
    current = 0
    check   = today
    for d in sorted(dates, reverse=True):
        if d == check or d == check - timedelta(days=1):
            current += 1
            check    = d
        else:
            break

    # Longest streak
    longest = 1
    streak  = 1
    sorted_dates = sorted(dates)
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1

    return {"current": current, "longest": longest, "total_days": len(dates)}


# ────────────────────────────────────────────────────────────────────────────
# TOPIC FREQUENCY
# ────────────────────────────────────────────────────────────────────────────
def get_top_topics(user_id: int, top_n: int = 8) -> List[Dict[str, Any]]:
    """
    Extract the most frequently asked-about topics from question history.
    Uses simple keyword extraction (no NLP library needed).

    Returns:
        [{"topic": "machine learning", "count": 12}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT m.content FROM chat_messages m
           JOIN chat_sessions s ON s.id = m.session_id
           WHERE s.user_id = ? AND m.role = 'user'""",
        (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return []

    # Extract significant words (remove common stop words)
    stop_words = {
        "what", "is", "the", "how", "does", "do", "can", "a", "an", "of",
        "in", "to", "and", "or", "for", "this", "that", "it", "me", "i",
        "my", "please", "explain", "describe", "tell", "about", "with",
        "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "will", "would", "could", "should", "may", "might", "shall",
    }

    word_freq: Counter = Counter()
    for (content,) in rows:
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())
        for w in words:
            if w not in stop_words:
                word_freq[w] += 1

    return [
        {"topic": w.replace("_", " ").title(), "count": c}
        for w, c in word_freq.most_common(top_n)
    ]


# ────────────────────────────────────────────────────────────────────────────
# ACTIVITY HEATMAP DATA
# ────────────────────────────────────────────────────────────────────────────
def get_daily_activity(user_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get message counts per day for the last N days.
    Used to render the activity chart in the dashboard.

    Returns:
        [{"date": "2024-01-15", "messages": 12}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT DATE(m.created_at) as day, COUNT(*) as cnt
           FROM chat_messages m
           JOIN chat_sessions s ON s.id = m.session_id
           WHERE s.user_id = ? AND m.role = 'user'
             AND m.created_at >= DATE('now', ?)
           GROUP BY day ORDER BY day ASC""",
        (user_id, f"-{days} days")
    ).fetchall()
    conn.close()

    return [{"date": r[0], "messages": r[1]} for r in rows]


# ────────────────────────────────────────────────────────────────────────────
# MODE USAGE
# ────────────────────────────────────────────────────────────────────────────
def get_mode_distribution(user_id: int) -> Dict[str, int]:
    """
    How often the user studies in each learning mode.
    Returns: {"Beginner": 5, "Exam": 3, "Practical": 8, ...}
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT learning_mode, COUNT(*) FROM chat_sessions WHERE user_id=? GROUP BY learning_mode",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


# ────────────────────────────────────────────────────────────────────────────
# FULL STATS BUNDLE  — single call for the dashboard
# ────────────────────────────────────────────────────────────────────────────
def get_dashboard_data(user_id: int) -> Dict[str, Any]:
    """
    Aggregate all analytics into one dict for the dashboard tab.
    Single DB connection keeps it fast.
    """
    from utils.history import get_user_stats
    return {
        "stats":     get_user_stats(user_id),
        "streak":    get_study_streak(user_id),
        "topics":    get_top_topics(user_id),
        "activity":  get_daily_activity(user_id),
        "modes":     get_mode_distribution(user_id),
    }