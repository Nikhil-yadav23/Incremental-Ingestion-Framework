
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "input" / "events.jsonl"


def generate_sample_data():
    """Generate reproducible events for pipeline testing."""

    events = [
        {
            "event_id": "EVT001",
            "record_id": "CUST001",
            "updated_at": "2026-11-11T10:00:00+00:00",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {
                "name": "Rahul",
                "city": "Hyderabad",
                "status": "active"
            }
        },
        {
            "event_id": "EVT002",
            "record_id": "CUST001",
            "updated_at": "2026-11-11T11:00:00+00:00",
            "source_sequence": 2,
            "operation": "UPSERT",
            "payload": {
                "name": "Rahul",
                "city": "Bengaluru",
                "status": "active"
            }
        },
        {
            "event_id": "EVT003",
            "record_id": "CUST002",
            "updated_at": "2026-11-11T10:30:00+00:00",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {
                "name": "Priya",
                "city": "Chennai",
                "status": "active"
            }
        },
        {
            "event_id": "EVT004",
            "record_id": "CUST003",
            "updated_at": "2026-11-10T08:30:00+00:00",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {
                "name": "Arjun",
                "city": "Hyderabad",
                "status": "active"
            }
        },
        {
            "event_id": "EVT005",
            "record_id": "CUST002",
            "updated_at": "2026-11-11T12:00:00+00:00",
            "source_sequence": 2,
            "operation": "DELETE",
            "payload": None
        },
        {
            "event_id": "EVT002",
            "record_id": "CUST001",
            "updated_at": "2026-11-11T11:00:00+00:00",
            "source_sequence": 2,
            "operation": "UPSERT",
            "payload": {
                "name": "Rahul",
                "city": "Bengaluru",
                "status": "active"
            }
        },
        {
            "event_id": "EVT006",
            "record_id": "",
            "updated_at": "2026-11-11T13:00:00+00:00",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {
                "name": "Invalid Customer"
            }
        }
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

        # Add malformed JSON to test error handling
        file.write('{"event_id": "BROKEN", invalid_json}\n')

    print(f"Generated {len(events) + 1} source lines.")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_sample_data()
