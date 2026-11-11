
from app.validation.rules import validate_event


def valid_event():
    return {
        "event_id": "EVT100",
        "record_id": "CUST100",
        "updated_at": "2026-11-11T10:00:00+00:00",
        "source_sequence": 1,
        "operation": "UPSERT",
        "payload": {
            "name": "Test Customer",
            "city": "Hyderabad"
        }
    }


def test_valid_event():
    result, reason = validate_event(valid_event())

    assert result is True
    assert reason is None


def test_missing_event_id():
    event = valid_event()
    event.pop("event_id")

    result, reason = validate_event(event)

    assert result is False
    assert "event_id" in reason


def test_empty_record_id():
    event = valid_event()
    event["record_id"] = ""

    result, reason = validate_event(event)

    assert result is False


def test_invalid_timestamp():
    event = valid_event()
    event["updated_at"] = "invalid-date"

    result, reason = validate_event(event)

    assert result is False


def test_timestamp_without_timezone():
    event = valid_event()
    event["updated_at"] = "2026-11-11T10:00:00"

    result, reason = validate_event(event)

    assert result is False


def test_invalid_operation():
    event = valid_event()
    event["operation"] = "REMOVE"

    result, reason = validate_event(event)

    assert result is False


def test_missing_payload():
    event = valid_event()
    event["payload"] = None

    result, reason = validate_event(event)

    assert result is False


def test_delete_without_payload():
    event = valid_event()
    event["operation"] = "DELETE"
    event["payload"] = None

    result, reason = validate_event(event)

    assert result is True
