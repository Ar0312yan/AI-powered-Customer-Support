import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "supportiq.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tickets (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id         TEXT UNIQUE NOT NULL,
            timestamp         TEXT,
            customer_id       TEXT,
            channel           TEXT,
            message           TEXT NOT NULL,
            agent_reply       TEXT,
            product           TEXT,
            order_value       REAL DEFAULT 0,
            customer_country  TEXT,
            resolution_status TEXT,
            category          TEXT,
            sentiment         TEXT,
            frustration_score INTEGER,
            priority          TEXT,
            revenue_risk      REAL DEFAULT 0,
            suggested_response TEXT,
            created_at        TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_category  ON tickets(category);
        CREATE INDEX IF NOT EXISTS idx_sentiment ON tickets(sentiment);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON tickets(timestamp);
    """)
    conn.commit()
    conn.close()


def save_tickets(tickets: list[dict]):
    conn = get_connection()
    conn.executemany("""
        INSERT OR REPLACE INTO tickets (
            ticket_id, timestamp, customer_id, channel, message,
            agent_reply, product, order_value, customer_country,
            resolution_status, category, sentiment, frustration_score,
            priority, revenue_risk, suggested_response
        ) VALUES (
            :ticket_id, :timestamp, :customer_id, :channel, :message,
            :agent_reply, :product, :order_value, :customer_country,
            :resolution_status, :category, :sentiment, :frustration_score,
            :priority, :revenue_risk, :suggested_response
        )
    """, tickets)
    conn.commit()
    conn.close()


def query(sql: str, params=()) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count() -> int:
    conn = get_connection()
    result = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    conn.close()
    return result
