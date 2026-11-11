
import sqlite3

import pytest

from app.publishing.publisher import publish_event


def setup_database():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute("""
        CREATE TABLE target_records (
            record_id TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL,
            source_sequence INTEGER NOT NULL,
            payload_json TEXT,
            is_deleted INTEGER NOT NULL,
            last_event_id TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE processed_events (
            event_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            processed_at TEXT NOT NULL
        )
    """)

    return connection


def make_event():
    return {
        "event_id": "EVT_RECOVERY",
        "record_id": "CUST_RECOVERY",
        "updated_at": "2026-11-11T10:00:00+00:00",
        "source_sequence": 1,
        "operation": "UPSERT",
        "payload_json": '{"name": "Recovery Test"}'
    }


def test_partial_failure_rolls_back_changes():
    connection = setup_database()
    event = make_event()

    with pytest.raises(RuntimeError):
        connection.execute("BEGIN")

        publish_event(connection, event, "RUN1")

        # Simulate a failure after publishing.
        raise RuntimeError("Simulated pipeline failure")

    connection.rollback()

    target_count = connection.execute(
        "SELECT COUNT(*) FROM target_records"
    ).fetchone()[0]

    processed_count = connection.execute(
        "SELECT COUNT(*) FROM processed_events"
    ).fetchone()[0]

    assert target_count == 0
    assert processed_count == 0

    connection.close()


def test_retry_after_failure_succeeds():
    connection = setup_database()
    event = make_event()

    connection.execute("BEGIN")

    publish_event(connection, event, "RUN1")
    connection.rollback()

    # Retry the same event after rollback.
    connection.execute("BEGIN")

    result = publish_event(connection, event, "RUN2")
    connection.commit()

    target_count = connection.execute(
        "SELECT COUNT(*) FROM target_records"
    ).fetchone()[0]

    processed_count = connection.execute(
        "SELECT COUNT(*) FROM processed_events"
    ).fetchone()[0]

    assert result == "inserted"
    assert target_count == 1
    assert processed_count == 1

    connection.close()
