
import sqlite3

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


def make_event(event_id, updated_at, city):
    return {
        "event_id": event_id,
        "record_id": "CUST100",
        "updated_at": updated_at,
        "source_sequence": 1,
        "operation": "UPSERT",
        "payload_json": '{"city": "' + city + '"}'
    }


def test_duplicate_event_is_not_inserted_twice():
    connection = setup_database()
    event = make_event(
        "EVT100",
        "2026-11-11T10:00:00+00:00",
        "Hyderabad"
    )

    first_result = publish_event(connection, event, "RUN1")
    second_result = publish_event(connection, event, "RUN2")

    count = connection.execute(
        "SELECT COUNT(*) FROM target_records"
    ).fetchone()[0]

    assert first_result == "inserted"
    assert second_result == "duplicate"
    assert count == 1

    connection.close()


def test_older_event_cannot_overwrite_newer_record():
    connection = setup_database()

    newer_event = make_event(
        "EVT102",
        "2026-11-11T12:00:00+00:00",
        "Bengaluru"
    )

    older_event = make_event(
        "EVT101",
        "2026-11-11T10:00:00+00:00",
        "Hyderabad"
    )

    publish_event(connection, newer_event, "RUN1")
    result = publish_event(connection, older_event, "RUN2")

    record = connection.execute(
        "SELECT payload_json FROM target_records "
        "WHERE record_id = 'CUST100'"
    ).fetchone()

    assert result == "stale"
    assert "Bengaluru" in record["payload_json"]
    assert "Hyderabad" not in record["payload_json"]

    connection.close()
