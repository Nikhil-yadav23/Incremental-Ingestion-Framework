
# Incremental Data Ingestion Framework

A watermark-based incremental data ingestion framework built with Python, FastAPI, SQLite, React, and Vite.

The framework processes source events, validates records, handles updates and deletes, detects duplicates, and publishes reliable data into a target database.

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

The application follows a three-layer architecture:

1. **Frontend:** React dashboard displays pipeline metrics, target records, rejected records, and run history.
2. **Backend:** FastAPI handles API requests and coordinates ingestion, validation, transformation, and publishing.
3. **Database:** SQLite stores source events, target records, processed events, watermarks, pipeline runs, and rejected records.

### Data Flow

Source JSONL Events → Extraction → Validation → Transformation → Publishing → SQLite Target Tables → Dashboard

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
Uses a persisted watermark containing the last processed timestamp and event ID. A seven-day lookback window helps discover late-arriving events.

### Idempotency
Uses unique event IDs and processed-event tracking to prevent duplicate processing.

### Out-of-Order Events
Compares event timestamps, source sequence numbers, and event IDs to prevent older events from overwriting newer records.

### Delete Handling
Uses tombstones to mark records as deleted instead of physically removing them.

### Failure Recovery
Uses SQLite transactions to ensure publishing and watermark updates are committed together or rolled back together.

### Data Quality
Validates required fields, timestamps, operations, sequence numbers, and payloads. Invalid records are stored with rejection reasons.

### Monitoring
Tracks rows read, inserted, updated, deleted, rejected, successful runs, and failed runs.

## 5. Project Structure

```text
CandidateWorkspace/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── config/
│   │   ├── database/
│   │   ├── ingestion/
│   │   ├── monitoring/
│   │   ├── publishing/
│   │   ├── transformation/
│   │   └── validation/
│   ├── scripts/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── database/
│   └── schema.sql
├── data/
│   ├── input/
│   ├── sample/
│   └── generated/
├── docs/
├── frontend/
├── reports/
├── .env.example
├── .gitignore
└── README.md
```

## 6. Setup and Execution

### Backend

Open a terminal:

```powershell
cd backend
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Backend API:
`http://127.0.0.1:8000`

Swagger documentation:
`http://127.0.0.1:8000/docs`

### Frontend

Open another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend dashboard:
`http://localhost:5173`

## 7. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check backend health |
| POST | `/api/run` | Execute ingestion pipeline |
| GET | `/api/metrics` | Retrieve pipeline metrics |
| GET | `/api/records` | View target records |
| GET | `/api/rejections` | View rejected records |
| GET | `/api/runs` | View pipeline run history |

## 8. Testing

Run the complete test suite:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest -v
```

Tests cover:

- Event validation.
- Missing and invalid fields.
- Duplicate event prevention.
- Out-of-order event handling.
- Transaction rollback.
- Retry after failure.

## 9. Sample Execution

The sample input is available in:

`data/input/events.jsonl`

The generator is available in:

`backend/scripts/generator.py`

The dashboard displays execution metrics and the resulting target records.

## 10. Design Decisions

- SQLite provides a simple local database without external infrastructure.
- Watermarks reduce unnecessary processing while a lookback window helps capture late-arriving records.
- Event IDs provide deduplication.
- Version comparison protects against stale updates.
- Tombstones preserve delete history.
- Database transactions support atomic publishing and recovery.

## 11. Future Improvements

- Support external database and cloud storage destinations.
- Add configurable watermark and lookback settings.
- Process large source files in batches or streams.
- Add automated performance benchmarks.
- Add configurable retry policies and dead-letter handling.

## 12. Conclusion

This project demonstrates an incremental data ingestion pipeline with watermark tracking, data validation, idempotent publishing, late-arriving event handling, tombstone-based deletes, transaction recovery, and operational monitoring.
