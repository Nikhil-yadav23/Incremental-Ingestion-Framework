# Design Decisions

## 1. Overview

This document explains the major technology and architectural decisions made while developing the Incremental Data Ingestion Framework.

The primary design goals are correctness, reliability, maintainability, idempotency, recoverability, and ease of execution.

## 2. Technology Selection

### Python – Backend Language

**Decision:** Python

**Reason:**
- Simple and readable syntax.
- Suitable for data processing and ingestion workloads.
- Provides useful libraries for validation, JSON handling, database operations, and API development.
- Makes the framework easier to extend.

### FastAPI – Backend Framework

**Decision:** FastAPI

**Reason:**
- Provides lightweight REST API development.
- Supports automatic API documentation through Swagger UI.
- Integrates well with Python.
- Supports structured request handling and HTTP communication with the frontend.

### React and Vite – Frontend

**Decision:** React with Vite

**Reason:**
- React supports reusable user-interface components.
- Vite provides a fast development environment.
- Enables a dashboard for pipeline execution and monitoring.
- Separates frontend responsibilities from backend processing logic.

### SQLite – Database

**Decision:** SQLite

**Reason:**
- Does not require a separate database server.
- Easy to configure and run locally.
- Supports transactions and primary-key constraints.
- Suitable for a reproducible hackathon demonstration.
- Reduces infrastructure setup requirements.

**Trade-off:**

SQLite is appropriate for this local implementation, but a production deployment with high concurrent write workloads or distributed processing may require PostgreSQL or another managed database.

### JSON Lines – Source Data Format

**Decision:** JSONL (`.jsonl`)

**Reason:**
- Each line represents an independent JSON event.
- Easy to inspect and modify for testing.
- Supports reproducible sample data.
- Allows malformed records to be identified and rejected individually.

**Trade-off:**

The current extractor reads the input file into memory. Large-scale ingestion would benefit from streaming or batch-based reading.

## 3. Watermark-Based Incremental Processing

**Decision:** Use source update timestamps and event identifiers as processing checkpoints.

**Reason:**
- Avoids relying only on full historical processing.
- Tracks pipeline progress between executions.
- Supports records arriving later than their original update timestamp.

The implementation uses a seven-day lookback window to capture late-arriving events.

**Trade-off:**

Records arriving later than the configured lookback period require a backfill or an adjusted lookback configuration.

## 4. Idempotent Publishing

**Decision:** Use event identifiers, processed-event tracking, and database upsert operations.

**Reason:**
- Prevents duplicate event processing.
- Makes repeated pipeline executions safer.
- Prevents older source versions from overwriting newer target records.

A source version is compared using its update timestamp, source sequence, and event identifier.

## 5. Tombstone-Based Deletion

**Decision:** Represent deletion using a tombstone instead of physically removing the target record.

**Reason:**
- Preserves deletion information.
- Prevents older events from accidentally restoring deleted records.
- Makes deleted records visible for auditing and monitoring.

The `is_deleted` column indicates whether a target record is active or deleted.

## 6. Transactional Processing and Recovery

**Decision:** Use SQLite database transactions for publishing and checkpoint updates.

**Reason:**
- Prevents partially committed database changes.
- Keeps target updates and watermark progress consistent.
- Allows failed processing transactions to be rolled back.
- Supports safe retry after a failure.

Failed pipeline runs are recorded separately so their status remains visible.

## 7. Data Validation and Rejection Handling

**Decision:** Validate records before publishing them.

**Reason:**
- Prevents malformed records from entering the target table.
- Identifies missing or invalid fields.
- Preserves rejected source data and rejection reasons.
- Helps investigate data-quality problems.

Invalid records are stored in the `rejected_records` table.

## 8. Monitoring and Observability

**Decision:** Store execution metrics and expose them through backend APIs.

**Reason:**
- Makes pipeline execution visible.
- Helps identify successful and failed runs.
- Tracks inserted, updated, deleted, and rejected records.
- Helps evaluate processing behavior across repeated runs.

The frontend dashboard displays these metrics and the associated records.

## 9. Testing Strategy

**Decision:** Use pytest for automated testing.

**Reason:**
- Tests validation rules.
- Checks duplicate-event handling.
- Verifies older events cannot overwrite newer records.
- Tests transaction rollback and retry behavior.

The current automated test suite contains 12 tests.

## 10. Future Improvements

Potential enhancements include:

- Streaming and batch-based source extraction.
- External database and API connectors.
- Configurable lookback windows.
- Scheduled pipeline execution.
- Structured logging and more detailed operational monitoring.
- Cloud deployment.
- Additional end-to-end integration and performance tests.

## 11. Conclusion

The framework prioritizes reliable incremental data processing while keeping the implementation simple enough to run and reproduce locally.

The technology choices and processing strategies provide a foundation that can be extended into a larger production-oriented ingestion system.