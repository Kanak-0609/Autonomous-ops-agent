"""
Persistent memory: logs every processed email + outcome to a real Postgres
database (Neon), keyed by sender email. This lets agents pull "past
interactions with this client" into context on future runs.
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id SERIAL PRIMARY KEY,
            sender_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            classification TEXT NOT NULL,
            outcome TEXT NOT NULL,
            summary TEXT NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def log_interaction(sender_email: str, subject: str, classification: str, outcome: str, summary: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO interactions (sender_email, subject, classification, outcome, summary, timestamp) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (sender_email, subject, classification, outcome, summary, datetime.now(timezone.utc)),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_past_interactions(sender_email: str, limit: int = 3) -> list[dict]:
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM interactions WHERE sender_email = %s ORDER BY timestamp DESC LIMIT %s",
        (sender_email, limit),
    )
    rows = cur.fetchall()
    cur.close()
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
    print("Logged to Postgres. Past interactions for Sarah:")
    for row in get_past_interactions("sarah.jones@acmewidgets.com"):
        print(f"  [{row['timestamp']}] {row['subject']} -> {row['outcome']}: {row['summary']}")