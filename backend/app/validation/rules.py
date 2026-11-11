
from datetime import datetime


REQUIRED_FIELDS = [
    "event_id",
    "record_id",
    "updated_at",
    "operation",
    "source_sequence",
]


def validate_event(event):
    """Validate one incoming source event."""

    if not isinstance(event, dict):
        return False, "Record must be a JSON object"

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in event or event[field] is None:
            return False, f"Missing required field: {field}"

    # Validate identifiers
    if not str(event["event_id"]).strip():
        return False, "event_id cannot be empty"

    if not str(event["record_id"]).strip():
        return False, "record_id cannot be empty"

    # Validate timestamp
    try:
        timestamp = datetime.fromisoformat(
            str(event["updated_at"]).replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            return False, "updated_at must include timezone"

    except (ValueError, TypeError):
        return False, "Invalid updated_at timestamp"

    # Validate operation
    operation = event["operation"]

    if operation not in ("UPSERT", "DELETE"):
        return False, "Operation must be UPSERT or DELETE"

    # Validate sequence
    if not isinstance(event["source_sequence"], int) or isinstance(
        event["source_sequence"], bool
    ) or event["source_sequence"] < 1:
        return False, "source_sequence must be a positive integer"

    # UPSERT requires a payload
    if operation == "UPSERT":
        if not isinstance(event.get("payload"), dict):
            return False, "UPSERT requires a valid payload object"

    return True, None
