# Data Dictionary

## 1. Overview

The Incremental Data Ingestion Framework uses SQLite to store source events, published records, processing checkpoints, execution history, and data-quality issues.

This document describes the database tables, columns, data types, keys, and their purposes.

## 2. Database Tables

The database contains six main tables:

1. `source_events`
2. `target_records`
3. `processed_events`
4. `watermarks`
5. `pipeline_runs`
6. `rejected_records`

---

## 3. Table: source_events

**Purpose:** Stores source events received by the ingestion framework.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| event_id | TEXT | Primary Key | Unique identifier for a source event |
| record_id | TEXT | NOT NULL | Identifier of the business record |
| updated_at | TEXT | NOT NULL | Source record update timestamp |
| source_sequence | INTEGER | NOT NULL, DEFAULT 1 | Version sequence for ordering events |
| operation | TEXT | NOT NULL, CHECK | Operation type: UPSERT or DELETE |
| payload_json | TEXT | Optional | Source record data in JSON format |
| received_at | TEXT | NOT NULL | Time the event was received |
| source_file | TEXT | Optional | Name or path of the source file |

**Index:** `idx_source_events_updated` on `updated_at` and `event_id` supports timestamp-based event lookup and ordering.

## 4. Table: target_records

**Purpose:** Stores the latest published state of each business record.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| record_id | TEXT | Primary Key | Unique business record identifier |
| updated_at | TEXT | NOT NULL | Timestamp of the applied source version |
| source_sequence | INTEGER | NOT NULL | Sequence number of the applied version |
| payload_json | TEXT | Optional | Published record data in JSON format |
| is_deleted | INTEGER | NOT NULL, DEFAULT 0 | Indicates whether the record is deleted |
| last_event_id | TEXT | NOT NULL | Event responsible for the latest state |

The `is_deleted` column represents tombstones:

- `0` means the record is active.
- `1` means the record has been deleted.

Deleted records remain in the target table to preserve deletion state.

## 5. Table: processed_events

**Purpose:** Tracks events that have already been processed to support idempotency.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| event_id | TEXT | Primary Key | Unique processed event identifier |
| run_id | TEXT | NOT NULL | Pipeline execution that processed the event |
| processed_at | TEXT | NOT NULL | Time the event was processed |

The primary key on `event_id` prevents the same event from being recorded as processed more than once.

## 6. Table: watermarks

**Purpose:** Maintains the processing checkpoint for each pipeline.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| pipeline_name | TEXT | Primary Key | Unique pipeline identifier |
| last_updated_at | TEXT | NOT NULL | Latest processed source update timestamp |
| last_event_id | TEXT | NOT NULL | Event identifier used as a checkpoint tie-breaker |

The watermark helps the pipeline identify its progress between executions.

## 7. Table: pipeline_runs

**Purpose:** Stores pipeline execution history and processing metrics.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| run_id | TEXT | Primary Key | Unique execution identifier |
| started_at | TEXT | NOT NULL | Pipeline start timestamp |
| finished_at | TEXT | Optional | Pipeline completion timestamp |
| status | TEXT | NOT NULL | Execution status |
| rows_read | INTEGER | DEFAULT 0 | Number of source rows read |
| inserted | INTEGER | DEFAULT 0 | Number of records inserted |
| updated | INTEGER | DEFAULT 0 | Number of records updated |
| deleted | INTEGER | DEFAULT 0 | Number of records marked deleted |
| rejected | INTEGER | DEFAULT 0 | Number of rejected records |
| error_message | TEXT | Optional | Error details when execution fails |

These metrics are used by the monitoring dashboard.

## 8. Table: rejected_records

**Purpose:** Maintains an audit history of invalid source records.

| Column | Data Type | Key / Constraint | Description |
|---|---|---|---|
| reject_id | INTEGER | Primary Key, AUTOINCREMENT | Unique rejection entry identifier |
| run_id | TEXT | NOT NULL | Pipeline execution associated with the rejection |
| event_id | TEXT | Optional | Event identifier, if available |
| reason | TEXT | NOT NULL | Reason the record was rejected |
| raw_json | TEXT | Optional | Original source data for investigation |
| rejected_at | TEXT | NOT NULL | Time the record was rejected |

Rejected records are retained for troubleshooting and data-quality analysis.

## 9. Key Relationships and Data Integrity

- `event_id` uniquely identifies an event in `source_events`.
- `record_id` uniquely identifies a published record in `target_records`.
- `event_id` in `processed_events` prevents duplicate event processing.
- `pipeline_name` identifies each pipeline's watermark.
- `run_id` connects execution metrics and rejected-record audit entries to a pipeline run.

The current schema does not define explicit foreign-key constraints between the run, rejection, and processed-event tables. These relationships are maintained through identifiers in application logic.

## 10. Data Type Conventions

- **TEXT:** Used for identifiers, timestamps, JSON payloads, statuses, and messages.
- **INTEGER:** Used for sequence numbers, metrics, deletion flags, and numeric identifiers.

Timestamps are stored as ISO 8601 text values. Event timestamps are validated to include timezone information and normalized to UTC during transformation.

## 11. Summary

The database design separates incoming source events, published target state, processing checkpoints, execution metrics, and rejected records.

This separation supports incremental processing, duplicate prevention, tombstone-based deletion, monitoring, and troubleshooting.