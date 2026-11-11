
import json
import uuid

from datetime import datetime, timezone, timedelta

from app.database.connection import (
    get_connection,
    initialize_database
)

from app.ingestion.extractor import extract_events

from app.ingestion.watermark import (
    get_watermark,
    update_watermark
)

from app.validation.rules import validate_event
from app.transformation.transformer import transform_event
from app.publishing.publisher import publish_event


PIPELINE_NAME = "customer_ingestion"
LOOKBACK_DAYS = 7


def run_pipeline():
    """Execute an incremental, idempotent ingestion run."""

    initialize_database()

    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    metrics = {
        "run_id": run_id,
        "status": "running",
        "rows_read": 0,
        "inserted": 0,
        "updated": 0,
        "deleted": 0,
        "rejected": 0,
        "duplicates": 0,
        "stale": 0,
    }

    try:
        # Create pipeline run history
        connection.execute(
            """
            INSERT INTO pipeline_runs (
                run_id, started_at, status
            )
            VALUES (?, ?, 'running')
            """,
            (run_id, started_at)
        )
        connection.commit()

        # 1. Read the previous successful watermark
        previous_watermark = get_watermark(
            connection,
            PIPELINE_NAME
        )

        # 2. Extract source events
        events = extract_events()

        # 3. Apply incremental extraction with lookback
        if previous_watermark:

            watermark_time = datetime.fromisoformat(
                previous_watermark[0]
            )

            cutoff_time = (
                watermark_time -
                timedelta(days=LOOKBACK_DAYS)
            )

            filtered_events = []

            for event in events:

                # Keep malformed records for rejection reporting
                if "_error" in event:
                    filtered_events.append(event)
                    continue

                try:
                    event_time = datetime.fromisoformat(
                        event["updated_at"].replace(
                            "Z", "+00:00"
                        )
                    )

                    if event_time >= cutoff_time:
                        filtered_events.append(event)

                except (ValueError, TypeError, KeyError):
                    filtered_events.append(event)

            events = filtered_events

        metrics["rows_read"] = len(events)

        # 4. Sort events deterministically
        events.sort(
            key=lambda event: (
                str(event.get("updated_at", "")),
                str(event.get("event_id", ""))
            )
        )

        latest_watermark = previous_watermark

        # 5. Begin atomic publishing transaction
        connection.execute("BEGIN")

        for event in events:

            # 6. Validate incoming event
            if "_error" in event:
                is_valid = False
                reason = event["_error"]

            else:
                is_valid, reason = validate_event(event)

            if not is_valid:

                connection.execute(
                    """
                    INSERT INTO rejected_records (
                        run_id,
                        event_id,
                        reason,
                        raw_json,
                        rejected_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        event.get("event_id"),
                        reason,
                        json.dumps(event, default=str),
                        datetime.now(timezone.utc).isoformat()
                    )
                )

                metrics["rejected"] += 1
                continue

            # 7. Transform event
            transformed = transform_event(event)

            # 8. Preserve raw source event
            connection.execute(
                """
                INSERT OR IGNORE INTO source_events (
                    event_id,
                    record_id,
                    updated_at,
                    source_sequence,
                    operation,
                    payload_json,
                    received_at,
                    source_file
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transformed["event_id"],
                    transformed["record_id"],
                    transformed["updated_at"],
                    transformed["source_sequence"],
                    transformed["operation"],
                    transformed["payload_json"],
                    event["received_at"],
                    transformed["source_file"]
                )
            )

            # 9. Publish using idempotent version checks
            action = publish_event(
                connection,
                transformed,
                run_id
            )

            if action in metrics:
                metrics[action] += 1

            # 10. Track latest successfully handled source position
            event_position = (
                transformed["updated_at"],
                transformed["event_id"]
            )

            if (
                latest_watermark is None
                or event_position > latest_watermark
            ):
                latest_watermark = event_position

        # 11. Update watermark in the same transaction
        if latest_watermark:
            update_watermark(
                connection,
                latest_watermark[0],
                latest_watermark[1],
                PIPELINE_NAME
            )

        # 12. Complete run history
        finished_at = datetime.now(timezone.utc).isoformat()

        connection.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = ?,
                status = 'completed',
                rows_read = ?,
                inserted = ?,
                updated = ?,
                deleted = ?,
                rejected = ?
            WHERE run_id = ?
            """,
            (
                finished_at,
                metrics["rows_read"],
                metrics["inserted"],
                metrics["updated"],
                metrics["deleted"],
                metrics["rejected"],
                run_id
            )
        )

        # Commit target changes, processed events and watermark together
        connection.commit()

        metrics["status"] = "completed"

    except Exception as error:

        # Roll back incomplete publishing and checkpoint changes
        connection.rollback()

        metrics["status"] = "failed"
        metrics["error"] = str(error)

        # Record failure separately
        connection.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = ?,
                status = 'failed',
                rows_read = ?,
                inserted = 0,
                updated = 0,
                deleted = 0,
                rejected = 0,
                error_message = ?
            WHERE run_id = ?
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                metrics["rows_read"],
                str(error),
                run_id
            )
        )

        connection.commit()

    finally:
        connection.close()

    return metrics
