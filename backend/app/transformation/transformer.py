
import json
from datetime import datetime, timezone


def transform_event(event):
    """
    Normalize a validated source event
    before storing it in the database.
    """

    # Normalize timestamp to UTC
    timestamp = datetime.fromisoformat(
        event["updated_at"].replace("Z", "+00:00")
    )

    timestamp = timestamp.astimezone(timezone.utc)
    normalized_timestamp = timestamp.isoformat()

    # Serialize payload consistently
    payload = event.get("payload")

    payload_json = (
        json.dumps(payload, sort_keys=True)
        if payload is not None
        else None
    )

    return {
        "event_id": str(event["event_id"]).strip(),
        "record_id": str(event["record_id"]).strip(),
        "updated_at": normalized_timestamp,
        "source_sequence": event["source_sequence"],
        "operation": event["operation"],
        "payload_json": payload_json,
        "source_file": event.get("source_file"),
    }
