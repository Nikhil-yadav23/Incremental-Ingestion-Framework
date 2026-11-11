# Sample Execution Report

## 1. Overview

This report documents a sample execution of the Incremental Data Ingestion Framework.

The application processes JSONL source events, validates records, publishes changes to SQLite, and displays execution metrics through a React dashboard.

## 2. Execution Summary

The following results were observed after eight successful pipeline runs.

| Metric | Result |
|---|---:|
| Total Runs | 8 |
| Rows Read | 68 |
| Inserted | 4 |
| Updated | 1 |
| Deleted | 1 |
| Rejected | 16 |
| Successful Runs | 8 |
| Failed Runs | 0 |

The latest execution processed 9 source events, inserted 0 records, updated 0 records, deleted 0 records, and recorded 2 rejections.

## 3. Target Record Results

| Record ID | Status | Latest Value |
|---|---|---|
| CUST001 | Active | Rahul, Bengaluru |
| CUST002 | Deleted | Tombstone |
| CUST003 | Active | Arjun, Hyderabad |
| CUST004 | Active | Sneha, Mumbai |

## 4. Demonstrated Scenarios

### New Record Insertion

New customer events were published into the target records table.

### Record Update

CUST001 was updated to the newer version containing Bengaluru as its city.

### Delete Handling

CUST002 was marked as deleted using a tombstone rather than physically removed.

### Late-Arriving Event

EVT007 was processed as a late-arriving event within the configured seven-day lookback window. It created CUST004.

### Idempotency

A subsequent pipeline execution did not create duplicate target records for previously processed events.

### Invalid Data Handling

The pipeline recorded two invalid input cases:

- EVT006: Empty record_id.
- Malformed JSON: Invalid JSON on line 8.

These two invalid source events were recorded again during subsequent runs. Therefore, the total of 16 rejection entries represents repeated rejection history, not 16 unique invalid source events.

## 5. Conclusion

The observed executions demonstrate record insertion, updates, tombstone-based deletion, late-arriving event handling, duplicate prevention, data rejection tracking, and pipeline monitoring.

These results represent a local sample execution using JSONL input and SQLite.