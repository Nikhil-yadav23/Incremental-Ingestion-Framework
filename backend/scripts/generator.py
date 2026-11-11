
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_OUTPUT = PROJECT_ROOT / "data" / "input" / "events.jsonl"


def generate_sample_data():
    """Generate the original small sample dataset."""

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

    SAMPLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(SAMPLE_OUTPUT, "w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

        file.write('{"event_id": "BROKEN", invalid_json}\n')

    print(f"Generated {len(events) + 1} sample source lines.")
    print(f"Output: {SAMPLE_OUTPUT}")


def generate_large_dataset(record_count, seed=42, output_file=None,
                           include_edge_cases=True):
    """Generate a configurable, reproducible synthetic dataset."""

    if record_count < 1:
        raise ValueError("Record count must be greater than zero.")

    rng = random.Random(seed)

    if output_file is None:
        output_file = (
            PROJECT_ROOT / "data" / "generated"
            / f"events_{record_count}.jsonl"
        )
    else:
        output_file = Path(output_file)

        if not output_file.is_absolute():
            output_file = PROJECT_ROOT / output_file

    output_file.parent.mkdir(parents=True, exist_ok=True)

    names = ["Rahul", "Priya", "Arjun", "Sneha", "Ananya"]
    cities = ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Pune"]

    base_time = datetime(2026, 11, 1, tzinfo=timezone.utc)
    events = []

    customer_count = max(1, int(record_count * 0.8))

    for index in range(record_count):
        customer_number = (index % customer_count) + 1
        sequence = (index // customer_count) + 1

        event_time = base_time + timedelta(seconds=index * 10)

        operation = "DELETE" if index % 20 == 0 else "UPSERT"

        event = {
            "event_id": f"EVT{index + 1:09d}",
            "record_id": f"CUST{customer_number:09d}",
            "updated_at": event_time.isoformat(),
            "source_sequence": sequence,
            "operation": operation,
            "payload": None if operation == "DELETE" else {
                "name": rng.choice(names),
                "city": rng.choice(cities),
                "status": "active"
            }
        }

        events.append(event)

    # Shuffle the events to simulate out-of-order arrival.
    rng.shuffle(events)

    # Keep a few deliberate invalid records for testing.
    if include_edge_cases:
        events.append(events[0].copy())

        events.append({
            "event_id": "INVALID_MISSING_RECORD",
            "record_id": "",
            "updated_at": "2026-11-11T10:00:00+00:00",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {"name": "Invalid Customer"}
        })

        events.append({
            "event_id": "INVALID_TIMESTAMP",
            "record_id": "CUST_INVALID_1",
            "updated_at": "not-a-timestamp",
            "source_sequence": 1,
            "operation": "UPSERT",
            "payload": {"name": "Invalid Timestamp"}
        })

        events.append({
            "event_id": "INVALID_OPERATION",
            "record_id": "CUST_INVALID_2",
            "updated_at": "2026-11-11T10:00:00+00:00",
            "source_sequence": 1,
            "operation": "UNKNOWN",
            "payload": {"name": "Invalid Operation"}
        })

    with open(output_file, "w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

        if include_edge_cases:
            file.write('{"event_id": "BROKEN", invalid_json}\n')

    print("Large dataset generated successfully.")
    print(f"Valid generated events: {record_count}")
    print(f"Total source lines: {len(events) + int(include_edge_cases)}")
    print(f"Random seed: {seed}")
    print(f"Output: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample or large ingestion datasets."
    )

    parser.add_argument(
        "--count",
        type=int,
        help="Number of valid synthetic events to generate."
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)."
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Optional output file path for a large dataset."
    )

    parser.add_argument(
        "--no-edge-cases",
        action="store_true",
        help="Do not add deliberate invalid records."
    )

    args = parser.parse_args()

    if args.count is None:
        generate_sample_data()
    else:
        generate_large_dataset(
            record_count=args.count,
            seed=args.seed,
            output_file=args.output,
            include_edge_cases=not args.no_edge_cases
        )


if __name__ == "__main__":
    main()
