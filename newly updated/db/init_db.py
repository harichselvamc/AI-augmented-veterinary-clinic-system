# db/init_db.py
from __future__ import annotations

import os
import sqlite3

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def initialize_db() -> None:
    """(Re)create the SQLite database using schema_sqlite.sql."""
    # Ensure folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print("✅ Database initialized with all tables.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to initialize database: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_db()
