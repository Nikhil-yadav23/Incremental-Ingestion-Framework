# Incremental Data Ingestion Framework

A watermark-based incremental data ingestion framework built using Python, FastAPI, SQLite, React, and Vite.

The framework ingests source events, validates and transforms records, handles updates and deletes, detects duplicates, and publishes reliable data into a target database.

## 1. Problem Statement

Build an incremental ingestion framework that supports:

- Watermark-based incremental processing.
- Safe reruns without duplicate target records.
- Late-arriving and out-of-order events.
- Delete operations using tombstones.
- Recovery after partial failures.
- Data validation and rejection tracking.
- Pipeline monitoring and measurable execution metrics.

## 2. Architecture

The application follows a three-layer architecture.

1. **Frontend:** React dashboard displays pipeline metrics, target records, rejected records, and execution history.
2. **Backend:** FastAPI handles API requests and coordinates extraction, validation, transformation, publishing, and monitoring.
3. **Database:** SQLite stores source events, target records, processed events, watermarks, pipeline runs, and rejected records.

### Data Flow

Source JSONL Events → Extraction → Validation → Transformation → Publishing → SQLite Target Tables → Dashboard

### Processing Workflow

1. Extract events from the JSONL source file.
2. Validate required fields, timestamps, operations, sequence numbers, and payloads.
3. Reject invalid records and store their rejection reasons.
4. Transform valid events into a normalized representation.
5. Publish valid events using duplicate detection and version comparison.
6. Update the watermark and execution metrics within the database transaction.
7. Display execution results through the dashboard.

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Database | SQLite |
| Testing | Pytest |
| API Documentation | FastAPI Swagger UI |
| Version Control | Git, GitHub |

## 4. Key Features

### Incremental Processing

Maintains a persisted watermark containing the last processed update timestamp and event ID.

A seven-day lookback window is used to discover late-arriving events. Events within this window can be read again during subsequent executions, while processed-event tracking prevents duplicate processing.

### Idempotency

Uses unique event IDs and processed-event tracking to prevent an event from being published more than once.

### Out-of-Order Events

Compares update timestamps, source sequence numbers, and event IDs to prevent older versions from overwriting newer target records.

### Delete Handling

Uses tombstones to mark records as deleted instead of physically removing them from the target table.

### Failure Recovery

Uses SQLite transactions to keep publishing changes and watermark updates consistent. If a processing transaction fails, its changes are rolled back, allowing a subsequent retry.

### Data Quality

Validates required fields, timestamps, operations, sequence numbers, and payloads. Invalid records are stored with their rejection reasons and raw input.

### Monitoring

Tracks:

- Total pipeline runs.
- Rows read.
- Records inserted.
- Records updated.
- Records deleted.
- Records rejected.
- Successful and failed runs.

## 5. Project Structure

```text
CandidateWorkspace/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── database/
│   │   │   └── connection.py
│   │   ├── ingestion/
│   │   │   ├── extractor.py
│   │   │   └── watermark.py
│   │   ├── monitoring/
│   │   │   ├── logger.py
│   │   │   └── metrics.py
│   │   ├── publishing/
│   │   │   └── publisher.py
│   │   ├── transformation/
│   │   │   └── transformer.py
│   │   ├── validation/
│   │   │   └── rules.py
│   │   └── pipeline.py
│   ├── scripts/
│   │   └── generator.py
│   ├── tests/
│   │   ├── test_pipeline.py
│   │   ├── test_validation.py
│   │   ├── test_idempotency.py
│   │   └── test_recovery.py
│   ├── main.py
│   └── requirements.txt
├── database/
│   └── schema.sql
├── data/
│   ├── input/
│   │   └── events.jsonl
│   ├── sample/
│   └── generated/
├── docs/
│   ├── architecture/
│   │   └── architecture.md
│   ├── data_dictionary.md
│   ├── design_decisions.md
│   ├── setup_and_execution.md
│   └── testing_strategy.md
├── frontend/
├── reports/
├── .env.example
├── .gitignore
└── README.md
```

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

Generate sample data:

```powershell
.venv\Scripts\python.exe scripts/generator.py
```

Start the backend:

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend API:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

The SQLite database is initialized automatically when the backend starts.

### Frontend Setup

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

The current test suite contains 12 passing tests covering:

- Valid and invalid event validation.
- Missing and empty fields.
- Invalid timestamps and operations.
- Missing payloads.
- Duplicate event prevention.
- Out-of-order event handling.
- Transaction rollback.
- Retry after failure.

These tests verify validation, publishing idempotency, and transaction recovery behavior. They are not a complete end-to-end integration test suite.

## 10. Sample Execution

Sample input:

`data/input/events.jsonl`

Sample generator:

`backend/scripts/generator.py`

The sample data demonstrates:

- New record insertion.
- Record updates.
- Delete operations.
- Duplicate events.
- Late-arriving events.
- Invalid and malformed records.

The dashboard displays execution metrics, target records, rejected records, and run history.

## 11. Design Decisions

- **SQLite:** Provides a lightweight local database without requiring external infrastructure.
- **Watermark and lookback:** Track processing progress while allowing late-arriving events within the configured lookback window to be discovered.
- **Event IDs:** Provide event-level duplicate detection.
- **Version comparison:** Protects target records from stale updates.
- **Tombstones:** Preserve delete information instead of physically removing records.
- **Transactions:** Keep publishing and watermark changes consistent.

## 12. Current Scope and Future Improvements

The current implementation is designed for reproducible local execution using JSONL input files and SQLite.

Potential improvements include:

- External source connectors.
- Cloud database and storage destinations.
- Configurable watermark and lookback settings.
- Batch or streaming processing for large datasets.
- Automated performance benchmarks.
- Configurable retry policies and dead-letter handling.

## 13. Conclusion

This project demonstrates an incremental data ingestion framework with watermark tracking, data validation, idempotent publishing, late-arriving event handling, tombstone-based deletes, transaction recovery, and operational monitoring.
