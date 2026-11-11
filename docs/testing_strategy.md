# Testing Strategy

## 1. Overview

The project uses automated tests with Pytest to verify data validation, idempotent publishing, and recovery behavior.

## 2. Test Coverage

The project currently contains 12 automated tests across three test modules.

| Test Module | Tests | Purpose |
|---|---:|---|
| test_validation.py | 8 | Validates required fields, timestamps, operations, and payloads |
| test_idempotency.py | 2 | Verifies duplicate-event prevention and stale-record protection |
| test_recovery.py | 2 | Verifies transaction rollback and successful retry |
| **Total** | **12** | |

## 3. Validation Tests

The validation tests cover:

- Valid event acceptance.
- Missing event ID.
- Empty record ID.
- Invalid timestamp.
- Timestamp without timezone.
- Invalid operation type.
- Missing UPSERT payload.
- DELETE event without a payload.

Invalid records should be rejected with a clear validation reason.

## 4. Idempotency Tests

The idempotency tests verify that:

- Processing the same event ID more than once does not create duplicate target records.
- An older source event cannot overwrite a newer target record.

## 5. Recovery Tests

The recovery tests verify that:

- A simulated failure rolls back database changes.
- Retrying after a failure successfully publishes the event.

These tests validate publishing and transaction behavior independently of a full end-to-end pipeline restart.

## 6. Running Tests

Open a terminal in the `backend` directory and run:

### Windows PowerShell

```powershell
.venv\Scripts\python.exe -m pytest -v
```

### Expected Result

```text
12 passed
```

## 7. Test Result

All 12 automated tests passed during local verification.

The tests help ensure that validation, duplicate prevention, version handling, and transaction recovery behave as expected.