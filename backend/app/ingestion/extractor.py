
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = PROJECT_ROOT / "data" / "input" / "events.jsonl"


def extract_events():
    """
    Read source events from a JSONL file.
    Each line represents one event.
    """

    events = []

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {INPUT_FILE}"
        )

    received_at = datetime.now(timezone.utc).isoformat()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            try:
                event = json.loads(line)

                if not isinstance(event, dict):
                    event = {
                        "_invalid_record": event,
                        "_error": "Record must be a JSON object"
                    }

                event["received_at"] = received_at
                event["source_file"] = INPUT_FILE.name
                events.append(event)

            except json.JSONDecodeError as error:
                events.append({
                    "_invalid_record": line.strip(),
                    "_error": f"Invalid JSON on line {line_number}: {error}"
                })

    return events
