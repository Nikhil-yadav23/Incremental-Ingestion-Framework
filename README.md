# Incremental Data Ingestion Framework

A watermark-based incremental data ingestion framework built using Python, FastAPI, SQLite, React, and Vite.

The framework ingests source events, validates and transforms records, handles inserts, updates, and deletes, detects duplicates, supports late-arriving data, and publishes reliable records into a target database.

## 1. Problem Statement

Build an incremental data ingestion framework that supports:

- Watermark-based processing.
- Safe reruns without duplicate target records.
- Late-arriving and out-of-order events.
- Delete operations using tombstones.
- Recovery after partial failures.
- Data validation and rejection tracking.
- Pipeline monitoring and measurable execution metrics.
- Reproducible sample data and scalable data generation.

## 2. Architecture

The application follows a three-layer architecture.

1. **Frontend:** React dashboard displays pipeline metrics, target records, rejected records, and execution history.
2. **Backend:** FastAPI handles API requests and coordinates extraction, validation, transformation, publishing, and monitoring.
3. **Database:** SQLite stores source events, target records, processed events, watermarks, pipeline runs, and rejected records.

### Data Flow

```text
Source JSONL Events
        |
        v
    Extraction
        |
        v
    Validation
        |
        v
  Transformation
        |
        v
    Publishing
        |
        v
  SQLite Target Tables
        |
        v
     Dashboard
```

### Processing Workflow

1. Extract events from the JSONL source file.
2. Validate required fields, timestamps, operations, sequence numbers, and payloads.
3. Reject invalid records and store their rejection reasons.
4. Transform valid events into a normalized representation.
5. Preserve source events for traceability.
6. Publish valid events using duplicate detection and version comparison.
7. Handle delete operations using tombstones.
8. Update the watermark and execution metrics within the database transaction.
9. Display execution results through the dashboard.

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Database | SQLite |
| Testing | Pytest |
| API Documentation | FastAPI Swagger UI |
| Data Generation | Python |
| Version Control | Git, GitHub |

## 4. Key Features

### Incremental Processing and Watermarks

Maintains a persisted watermark containing the latest processed update timestamp and event ID.

The current JSONL source adapter scans all available source events on each run to detect late-arriving records, including records with timestamps older than the existing watermark.

Previously processed event IDs are safely skipped, preventing duplicate publishing.

This is a correctness-first implementation. It supports late-arriving records without a fixed lookback limit, although scanning the complete source file on every run introduces additional processing overhead.

### Idempotency

Uses unique event IDs and processed-event tracking to prevent an event from being published more than once.

Repeated executions do not create duplicate target records for already processed events.

### Out-of-Order Event Handling

Compares update timestamps, source sequence numbers, and event IDs to prevent older versions from overwriting newer target records.

### Delete Handling

Uses tombstones to mark records as deleted instead of physically removing them from the target table.

This preserves deletion information for auditing and downstream processing.

### Failure Recovery

Uses SQLite transactions to keep publishing changes and watermark updates consistent.

If a processing transaction fails, its changes are rolled back. A subsequent retry can safely process the same events.

### Data Quality

Validates:

- Required event identifiers.
- Record identifiers.
- Update timestamps.
- Source sequence numbers.
- Supported operations.
- Payload structure.

Invalid records are stored in the rejected records table with their rejection reasons and raw input.

### Monitoring and Observability

Tracks:

- Total pipeline runs.
- Rows read.
- Records inserted.
- Records updated.
- Records deleted.
- Records rejected.
- Successful and failed runs.
- Execution status and error messages.

## 5. Project Structure

```text
CandidateWorkspace/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- routes.py
|   |   |-- config/
|   |   |   `-- settings.py
|   |   |-- database/
|   |   |   `-- connection.py
|   |   |-- ingestion/
|   |   |   |-- extractor.py
|   |   |   `-- watermark.py
|   |   |-- monitoring/
|   |   |   |-- logger.py
|   |   |   `-- metrics.py
|   |   |-- publishing/
|   |   |   `-- publisher.py
|   |   |-- transformation/
|   |   |   `-- transformer.py
|   |   |-- validation/
|   |   |   `-- rules.py
|   |   `-- pipeline.py
|   |
|   |-- scripts/
|   |   `-- generator.py
|   |
|   |-- tests/
|   |   |-- test_pipeline.py
|   |   |-- test_validation.py
|   |   |-- test_idempotency.py
|   |   `-- test_recovery.py
|   |
|   |-- main.py
|   `-- requirements.txt
|
|-- database/
|   `-- schema.sql
|
|-- data/
|   |-- input/
|   |   `-- events.jsonl
|   |-- sample/
|   `-- generated/
|
|-- docs/
|   |-- architecture/
|   |   `-- architecture.md
|   |-- data_dictionary.md
|   |-- design_decisions.md
|   |-- setup_and_execution.md
|   `-- testing_strategy.md
|
|-- frontend/
|
|-- reports/
|
|-- .env.example
|-- .gitignore
`-- README.md
```

Generated benchmark datasets and local SQLite database files are excluded from version control. They can be recreated locally using the generator and application.

## 6. Prerequisites

Install the following:

- Python 3.10 or later.
- Node.js and npm.
- Git.

## 7. Setup and Execution

### Clone the Repository

```bash
git clone https://github.com/Nikhil-yadav23/Incremental-Ingestion-Framework.git
cd Incremental-Ingestion-Framework
```

### Backend Setup

Open a terminal in the project root:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Generate Sample Data

```powershell
.venv\Scripts\python.exe scripts/generator.py
```

This generates the default sample input file at:

```text
data/input/events.jsonl
```

### Generate a Large Dataset

To generate 100,000 reproducible records:

```powershell
.venv\Scripts\python.exe scripts/generator.py --count 100000 --seed 42
```

The generated dataset is saved under:

```text
data/generated/
```

The generator supports configurable record counts and random seeds. It also includes deliberate edge cases when enabled.

### Start the Backend

From the backend directory:

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend API:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

The SQLite database is initialized automatically when the backend starts.

### Start the Frontend

Open another terminal in the project root:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend dashboard:

`http://localhost:5173`

## 8. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check backend health |
| POST | `/api/run` | Execute ingestion pipeline |
| GET | `/api/metrics` | Retrieve pipeline metrics |
| GET | `/api/records` | View target records |
| GET | `/api/rejections` | View rejected records |
| GET | `/api/runs` | View pipeline run history |

## 9. Testing

Run the automated test suite from the backend directory:

```powershell
.venv\Scripts\python.exe -m pytest -v
```

**Latest verified result: 12 tests passed.**

The test suite covers:

- Valid and invalid event validation.
- Missing and empty fields.
- Invalid timestamps and operations.
- Missing payloads.
- Duplicate event prevention.
- Out-of-order event handling.
- Transaction rollback.
- Retry after failure.

These tests verify validation, publishing idempotency, and transaction recovery behavior. They are not a complete end-to-end integration test suite.

### Late-Arriving Event Verification

A separate test using an isolated SQLite database verified the following scenario:

1. Process a baseline event with an update timestamp of November 10, 2026.
2. Introduce a new event with an older update timestamp of October 1, 2026.
3. Rerun the pipeline.
4. Verify that the late-arriving event is inserted while the baseline event is skipped as a duplicate.
5. Confirm that both records exist in the target table and both event IDs exist in processed-event tracking.

Verified result:

| Metric | Result |
|---|---:|
| Events read | 2 |
| New late event inserted | 1 |
| Previously processed event skipped | 1 |
| Rejected | 0 |

## 10. Performance Benchmark

A local benchmark was performed using a reproducibly generated dataset of 100,000 records, with additional deliberate edge cases.

### Benchmark Results

| Measurement | Result |
|---|---:|
| Total input records | 100,005 |
| Inserted | 76,000 |
| Updated | 19,000 |
| Delete operations | 5,000 |
| Rejected | 4 |
| Duplicate events | 1 |
| Execution time | 3.72 seconds |
| Throughput | 26,873 records/second |

The benchmark completed successfully.

**Measurement note:** These results are from one local execution using Python, JSONL input, and SQLite. Execution time includes database initialization. Results depend on the execution environment and should not be interpreted as production performance guarantees.

### Rerun Verification

The same input was executed again against the same benchmark database.

The rerun produced:

- Zero new inserts.
- Zero new updates.
- Zero new delete operations.
- Previously processed events skipped as duplicates.
- No duplicate target records.

This demonstrates idempotent rerun behavior for the processed events.

## 11. Sample Execution

Sample input:

`data/input/events.jsonl`

Sample generator:

`backend/scripts/generator.py`

The sample and generated datasets support scenarios such as:

- New record insertion.
- Record updates.
- Delete operations.
- Duplicate events.
- Out-of-order events.
- Invalid records.
- Malformed JSON.

The dashboard displays execution metrics, target records, rejected records, and run history.

## 12. Design Decisions

- **SQLite:** Provides a lightweight local database without requiring external infrastructure.
- **Watermark tracking:** Persists processing progress and provides a reference for source update ordering.
- **Late-arrival handling:** The current JSONL adapter scans the complete source file on each run to avoid missing newly discovered records with older timestamps.
- **Event IDs:** Provide event-level duplicate detection.
- **Version comparison:** Protects target records from stale updates.
- **Tombstones:** Preserve delete information instead of physically removing records.
- **Transactions:** Keep publishing and watermark changes consistent.
- **Deterministic generation:** Fixed random seeds make benchmark datasets reproducible.

## 13. Current Scope and Future Improvements

The current implementation is designed for reproducible local execution using JSONL input files and SQLite.

Potential improvements include:

- External source connectors.
- Source-side arrival cursors or file-offset checkpoints to avoid rescanning complete files.
- Cloud database and storage destinations.
- Configurable watermark strategies and backfill policies.
- Batch or streaming processing for large datasets.
- More extensive end-to-end integration tests.
- Configurable retry policies and dead-letter handling.
- Repeated performance benchmarks across different dataset sizes.

## 14. Conclusion

This project demonstrates an incremental data ingestion framework with persisted watermark tracking, data validation, idempotent publishing, late-arriving event handling, tombstone-based deletes, transaction recovery, reproducible data generation, and operational monitoring.

It provides a locally runnable implementation with automated tests, measurable benchmark results, and documentation to support independent evaluation.
