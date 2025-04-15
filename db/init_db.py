# db/init_db.py

import sqlite3
import os

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_sqlite.sql")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def initialize_db():
    """Initialize the SQLite database with the schema."""
    if os.path.exists(DB_PATH):
        print("🔄 Database already exists. Overwriting...")

    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Database initialized with all tables.")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
    finally:
        conn.close()
