"""
Multi-tenant persistent storage on Postgres (Neon).

Every table is scoped by organization_id, so multiple businesses can use
the same running system with fully isolated data. This replaces the old
single-tenant version where "Bright Consulting" was hardcoded everywhere.
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
    """Creates all tables if they don't exist yet. Safe to call every run."""
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_config (
            organization_id INTEGER PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
            services TEXT NOT NULL DEFAULT '',
            standard_rate TEXT NOT NULL DEFAULT '',
            onboarding_rate TEXT NOT NULL DEFAULT '',
            availability TEXT NOT NULL DEFAULT '',
            response_policy TEXT NOT NULL DEFAULT '',
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id SERIAL PRIMARY KEY,
            organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
            sender_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            classification TEXT NOT NULL,
            outcome TEXT NOT NULL,
            summary TEXT NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL
        )
    """)

    # Add organization_id to interactions if the table pre-dates this migration
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='interactions' AND column_name='organization_id'
            ) THEN
                ALTER TABLE interactions ADD COLUMN organization_id INTEGER;
            END IF;
        END $$;
    """)

    conn.commit()
    cur.close()
    conn.close()


def get_or_create_organization(name: str, slug: str) -> int:
    """Returns the organization's id, creating it if it doesn't exist yet."""
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT id FROM organizations WHERE slug = %s", (slug,))
    row = cur.fetchone()
    if row:
        cur.close()
        conn.close()
        return row["id"]

    cur.execute(
        "INSERT INTO organizations (name, slug) VALUES (%s, %s) RETURNING id",
        (name, slug),
    )
    org_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return org_id


def set_company_config(
    organization_id: int,
    services: str,
    standard_rate: str,
    onboarding_rate: str,
    availability: str,
    response_policy: str,
):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO company_config (organization_id, services, standard_rate, onboarding_rate, availability, response_policy, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (organization_id) DO UPDATE SET
            services = EXCLUDED.services,
            standard_rate = EXCLUDED.standard_rate,
            onboarding_rate = EXCLUDED.onboarding_rate,
            availability = EXCLUDED.availability,
            response_policy = EXCLUDED.response_policy,
            updated_at = EXCLUDED.updated_at
        """,
        (organization_id, services, standard_rate, onboarding_rate, availability, response_policy, datetime.now(timezone.utc)),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_company_config(organization_id: int) -> dict | None:
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM company_config WHERE organization_id = %s", (organization_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def log_interaction(organization_id: int, sender_email: str, subject: str, classification: str, outcome: str, summary: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO interactions (organization_id, sender_email, subject, classification, outcome, summary, timestamp) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (organization_id, sender_email, subject, classification, outcome, summary, datetime.now(timezone.utc)),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_past_interactions(organization_id: int, sender_email: str, limit: int = 3) -> list[dict]:
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM interactions WHERE organization_id = %s AND sender_email = %s ORDER BY timestamp DESC LIMIT %s",
        (organization_id, sender_email, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    org_id = get_or_create_organization("Bright Consulting", "bright-consulting")
    print(f"Organization ready: id={org_id}")

    set_company_config(
        organization_id=org_id,
        services="Marketing strategy, social media management, brand consulting",
        standard_rate="$400/month for ongoing retainer clients (up to 10 hours/month)",
        onboarding_rate="$450/month for the first 3 months, then drops to standard rate",
        availability="Currently accepting 2 new clients starting next month",
        response_policy="Always be warm and professional. For billing questions, clarify onboarding vs standard rate. For new inquiries, mention availability and ask about needs before quoting.",
    )
    print("Company config saved.")

    config = get_company_config(org_id)
    print("Loaded config:", config)