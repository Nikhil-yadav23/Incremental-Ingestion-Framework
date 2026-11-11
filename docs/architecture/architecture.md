# System Architecture

## 1. Overview

The Incremental Data Ingestion Framework is designed to process source records using update timestamps and watermarks.

It supports incremental processing, late-arriving records, duplicate prevention, update operations, delete operations, data validation, and recovery after processing failures.

The application follows a three-tier architecture:

1. **Frontend:** React with Vite provides a dashboard for running and monitoring the pipeline.
2. **Backend:** Python with FastAPI handles ingestion, validation, transformation, publishing, and API requests.
3. **Database:** SQLite stores source events, target records, watermarks, pipeline execution history, processed events, and rejected records.

## 2. Architecture Flow

```text
              USER
                |
                v
       REACT FRONTEND (VITE)
                |
          HTTP API Requests
                |
                v
         FASTAPI BACKEND
                |
                v
       PIPELINE ORCHESTRATION
                |
       +--------+---------+
       |        |         |
       v        v         v
   EXTRACT   VALIDATE  TRANSFORM
       |        |         |
       +--------+---------+
                |
                v
            PUBLISH
                |
                v
          SQLITE DATABASE
                |
       +--------+---------+
       |        |         |
       v        v         v
    TARGET   WATERMARK  MONITORING
    RECORDS            AND REJECTS
```

## 3. Backend Processing Components

### Extraction
Reads source events from the JSON Lines input file and prepares them for processing.

### Watermark Management
Maintains the last successfully processed update timestamp and event ID. A seven-day lookback window is used to capture late-arriving records.

### Validation
Checks required fields, timestamps, operation types, sequence numbers, and payload requirements. Invalid records are stored in the rejection table.

### Transformation
Normalizes timestamps and serializes payloads into a consistent JSON representation.

### Publishing
Applies valid events to target records. It prevents duplicate event processing and uses source versions to avoid older events overwriting newer records. Delete operations are represented using tombstones.

### Monitoring
Stores pipeline run status, processing counts, errors, and rejected records for dashboard visibility.

## 4. Database Components

The SQLite database contains the following tables:

- `source_events`: Stores ingested source events.
- `target_records`: Stores the latest published state of each record.
- `processed_events`: Tracks events already processed.
- `watermarks`: Stores pipeline progress.
- `pipeline_runs`: Maintains execution history and metrics.
- `rejected_records`: Stores invalid records and rejection reasons.

See [Data Dictionary](../data_dictionary.md) for the table definitions.

## 5. Frontend Components

The React dashboard communicates with the FastAPI backend through HTTP endpoints.

It allows users to:

- Execute the ingestion pipeline.
- View processing metrics.
- Inspect published target records.
- Identify rejected records.
- Review pipeline execution history.

## 6. Execution Sequence

1. The user starts the pipeline from the dashboard.
2. The frontend sends a request to the backend.
3. The backend initializes the database and creates a pipeline run.
4. The extractor reads source events.
5. The watermark and lookback logic determine which events are eligible for processing.
6. Validation checks each event.
7. Valid events are transformed and published.
8. Invalid events are recorded as rejected.
9. The watermark and run metrics are updated transactionally.
10. The frontend retrieves and displays the latest results.

## 7. Failure Handling

Database transactions protect publishing and watermark updates from partial commits.

If processing fails, the current transaction is rolled back and the failed run is recorded. A subsequent execution can retry the source events without duplicating successfully published target data.

## 8. Current Implementation Scope

The current implementation is designed for local execution using JSON Lines input files, FastAPI, and SQLite.

The architecture can be extended in the future to support external data sources, cloud databases, scheduled execution, and large-scale batch or streaming ingestion.