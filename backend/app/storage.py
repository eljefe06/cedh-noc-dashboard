from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator


def _connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str) -> sqlite3.Connection:
    conn = _connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS incidents (
            id          TEXT PRIMARY KEY,
            started_at  TEXT NOT NULL,
            resolved_at TEXT,
            status      TEXT NOT NULL DEFAULT 'open',
            severity    TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_name TEXT NOT NULL,
            summary     TEXT NOT NULL,
            first_error TEXT
        );

        CREATE TABLE IF NOT EXISTS metric_snapshots (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            server_name  TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_metric_snapshots_server
            ON metric_snapshots(server_name, collected_at DESC);

        CREATE TABLE IF NOT EXISTS events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            occurred_at  TEXT NOT NULL,
            event_type   TEXT NOT NULL,
            target_name  TEXT NOT NULL,
            detail_json  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_events_occurred
            ON events(occurred_at DESC);

        CREATE TABLE IF NOT EXISTS status_cache (
            key         TEXT PRIMARY KEY,
            value_json  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


@contextmanager
def get_conn(conn: sqlite3.Connection) -> Generator[sqlite3.Connection, None, None]:
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


# ── status cache ──────────────────────────────────────────────────────────────

def cache_set(conn: sqlite3.Connection, key: str, value: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO status_cache(key, value_json, updated_at) VALUES(?,?,?)",
        (key, json.dumps(value), now),
    )
    conn.commit()


def cache_get(conn: sqlite3.Connection, key: str) -> dict | None:
    row = conn.execute(
        "SELECT value_json FROM status_cache WHERE key=?", (key,)
    ).fetchone()
    return json.loads(row["value_json"]) if row else None


# ── incidents ─────────────────────────────────────────────────────────────────

def incident_open(
    conn: sqlite3.Connection,
    *,
    id: str,
    severity: str,
    target_type: str,
    target_name: str,
    summary: str,
    first_error: str | None = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR IGNORE INTO incidents
           (id, started_at, status, severity, target_type, target_name, summary, first_error)
           VALUES(?,?,?,?,?,?,?,?)""",
        (id, now, "open", severity, target_type, target_name, summary, first_error),
    )
    conn.commit()


def incident_resolve(conn: sqlite3.Connection, id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE incidents SET status='resolved', resolved_at=? WHERE id=? AND status='open'",
        (now, id),
    )
    conn.commit()


def incidents_open_count(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM incidents WHERE status='open'"
    ).fetchone()
    return row["n"] if row else 0


def incidents_recent(conn: sqlite3.Connection, n: int = 20) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM incidents ORDER BY started_at DESC LIMIT ?", (n,)
    ).fetchall()
    return [dict(r) for r in rows]


def incidents_open_list(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM incidents WHERE status='open' ORDER BY started_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]
