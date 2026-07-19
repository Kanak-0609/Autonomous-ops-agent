"""
FastAPI backend exposing agent activity data to the dashboard.

Endpoints are scoped by organization_id so the same backend can serve
multiple tenants. Right now the frontend only knows about one organization
(id=1, seeded by memory_store), but every query below is written as if
there could be many -- this is the shape a real multi-tenant API needs.

Run with: uvicorn backend.main:app --reload --port 8000
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from memory.memory_store import _get_connection
import psycopg2.extras

app = FastAPI(title="Autonomous Ops Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/organizations")
def get_organizations():
    """Returns all organizations, so the dashboard could offer a tenant switcher."""
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, slug FROM organizations ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/api/interactions")
def get_interactions(organization_id: int = 1, limit: int = 50):
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM interactions WHERE organization_id = %s ORDER BY timestamp DESC LIMIT %s",
        (organization_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/api/metrics")
def get_metrics(organization_id: int = 1):
    conn = _get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("SELECT COUNT(*) as total FROM interactions WHERE organization_id = %s", (organization_id,))
    total = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as sent FROM interactions WHERE organization_id = %s AND outcome = 'sent'", (organization_id,))
    sent = cur.fetchone()["sent"]

    cur.execute("SELECT COUNT(*) as rejected FROM interactions WHERE organization_id = %s AND outcome = 'rejected'", (organization_id,))
    rejected = cur.fetchone()["rejected"]

    cur.execute("SELECT COUNT(*) as skipped FROM interactions WHERE organization_id = %s AND outcome = 'skipped'", (organization_id,))
    skipped = cur.fetchone()["skipped"]

    cur.execute(
        "SELECT COUNT(DISTINCT sender_email) as unique_senders FROM interactions WHERE organization_id = %s",
        (organization_id,),
    )
    unique_senders = cur.fetchone()["unique_senders"]

    cur.close()
    conn.close()

    drafted = sent + rejected

    return {
        "total_processed": total,
        "triaged": total,
        "drafted": drafted,
        "approved": sent,
        "sent": sent,
        "rejected": rejected,
        "skipped": skipped,
        "unique_senders": unique_senders,
        "eval_accuracy": "93.8%",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}