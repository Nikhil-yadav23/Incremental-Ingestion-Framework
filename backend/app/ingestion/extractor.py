
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_INPUT_FILE = PROJECT_ROOT / "data" / "input" / "events.jsonl"


def extract_events(input_file=None):
    """
    Read source events from a JSONL file.
    Each line represents one event.

    If no file is provided, use the default sample input.
    """

    source_file = (
        Path(input_file)
        if input_file is not None
        else DEFAULT_INPUT_FILE
    )

    if not source_file.is_absolute():
        source_file = PROJECT_ROOT / source_file

    if not source_file.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_file}"
        )

    events = []
    received_at = datetime.now(timezone.utc).isoformat()

    with open(source_file, "r", encoding="utf-8-sig") as file:
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
                event["source_file"] = source_file.name
                events.append(event)

            except json.JSONDecodeError as error:
                events.append({
                    "_invalid_record": line.strip(),
                    "_error": f"Invalid JSON on line {line_number}: {error}"
                })

    return events
