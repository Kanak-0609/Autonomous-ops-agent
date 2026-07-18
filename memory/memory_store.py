"""
Persistent memory: logs every processed email + outcome to a local SQLite
database, keyed by sender email. This lets agents pull "past interactions
with this client" into context on future runs.
"""

import sqlite3
from datetime import datetime, timezone

DB_PATH = "memory/agent_memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            classification TEXT NOT NULL,
            outcome TEXT NOT NULL,
            summary TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(sender_email: str, subject: str, classification: str, outcome: str, summary: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO interactions (sender_email, subject, classification, outcome, summary, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (sender_email, subject, classification, outcome, summary, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def get_past_interactions(sender_email: str, limit: int = 3) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM interactions WHERE sender_email = ? ORDER BY timestamp DESC LIMIT ?",
        (sender_email, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    log_interaction(
        sender_email="sarah.jones@acmewidgets.com",
        subject="Question about invoice #4412",
        classification="billing_question",
        outcome="sent",
        summary="Explained onboarding rate vs standard rate, confirmed she's in month 2 of 3.",
    )
    print("Logged. Past interactions for Sarah:")
    for row in get_past_interactions("sarah.jones@acmewidgets.com"):
        print(f"  [{row['timestamp']}] {row['subject']} -> {row['outcome']}: {row['summary']}")