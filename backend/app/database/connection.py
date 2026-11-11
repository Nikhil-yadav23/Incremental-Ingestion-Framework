
import sqlite3
from pathlib import Path


# Locate the CandidateWorkspace root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Default database and schema locations
DATABASE_PATH = PROJECT_ROOT / "data" / "ingestion.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def resolve_database_path(db_path=None):
    """Resolve a custom database path or use the default database."""

    if db_path is None:
        return DATABASE_PATH

    path = Path(db_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path


def get_connection(db_path=None):
    """Create a SQLite connection to the selected database."""

    database_file = resolve_database_path(db_path)
    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        database_file,
        timeout=30
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=None):
    """Initialize tables in the selected database."""

    database_file = resolve_database_path(db_path)
    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(database_file)

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

        connection.commit()
        print(f"Database initialized: {database_file}")

    finally:
        connection.close()
