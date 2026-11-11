
from datetime import datetime, timezone


def publish_event(connection, event, run_id):
    """
    Publish one transformed event into the target table.
    Returns the action performed.
    """

    now = datetime.now(timezone.utc).isoformat()

    # 1. Check whether this event was already processed
    existing_event = connection.execute(
        """
        SELECT event_id
        FROM processed_events
        WHERE event_id = ?
        """,
        (event["event_id"],)
    ).fetchone()

    if existing_event:
        return "duplicate"

    # 2. Get the current target record
    current = connection.execute(
        """
        SELECT updated_at, source_sequence, last_event_id
        FROM target_records
        WHERE record_id = ?
        """,
        (event["record_id"],)
    ).fetchone()

    incoming_version = (
        event["updated_at"],
        event["source_sequence"],
        event["event_id"]
    )

    # 3. Compare incoming version with target version
    if current:
        current_version = (
            current["updated_at"],
            current["source_sequence"],
            current["last_event_id"]
        )

        if incoming_version <= current_version:
            connection.execute(
                """
                INSERT INTO processed_events
                (event_id, run_id, processed_at)
                VALUES (?, ?, ?)
                """,
                (event["event_id"], run_id, now)
            )
            return "stale"

    # 4. Handle deletion using a tombstone
    is_deleted = 1 if event["operation"] == "DELETE" else 0

    payload_json = (
        None if is_deleted else event["payload_json"]
    )

    # 5. Insert or update target record
    connection.execute(
        """
        INSERT INTO target_records (
            record_id,
            updated_at,
            source_sequence,
            payload_json,
            is_deleted,
            last_event_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(record_id) DO UPDATE SET
            updated_at = excluded.updated_at,
            source_sequence = excluded.source_sequence,
            payload_json = excluded.payload_json,
            is_deleted = excluded.is_deleted,
            last_event_id = excluded.last_event_id
        """,
        (
            event["record_id"],
            event["updated_at"],
            event["source_sequence"],
            payload_json,
            is_deleted,
            event["event_id"]
        )
    )

    # 6. Record successful processing
    connection.execute(
        """
        INSERT INTO processed_events
        (event_id, run_id, processed_at)
        VALUES (?, ?, ?)
        """,
        (event["event_id"], run_id, now)
    )

    return "deleted" if is_deleted else (
        "inserted" if current is None else "updated"
    )
