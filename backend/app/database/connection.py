
import sqlite3
from pathlib import Path

# Locate the CandidateWorkspace root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Database file location
DATABASE_PATH = PROJECT_ROOT / "data" / "ingestion.db"

# SQL schema location
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def get_connection():
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create database tables using schema.sql."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

        connection.commit()
        print(f"Database initialized: {DATABASE_PATH}")

    finally:
        connection.close()
