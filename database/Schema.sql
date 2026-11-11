
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_events (
    event_id TEXT PRIMARY KEY,
    record_id TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    source_sequence INTEGER NOT NULL DEFAULT 1,
    operation TEXT NOT NULL CHECK (operation IN ('UPSERT', 'DELETE')),
    payload_json TEXT,
    received_at TEXT NOT NULL,
    source_file TEXT
);

CREATE INDEX IF NOT EXISTS idx_source_events_updated
ON source_events(updated_at, event_id);

CREATE TABLE IF NOT EXISTS target_records (
    record_id TEXT PRIMARY KEY,
    updated_at TEXT NOT NULL,
    source_sequence INTEGER NOT NULL,
    payload_json TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    last_event_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_events (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    processed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watermarks (
    pipeline_name TEXT PRIMARY KEY,
    last_updated_at TEXT NOT NULL,
    last_event_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    rows_read INTEGER DEFAULT 0,
    inserted INTEGER DEFAULT 0,
    updated INTEGER DEFAULT 0,
    deleted INTEGER DEFAULT 0,
    rejected INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS rejected_records (
    reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    event_id TEXT,
    reason TEXT NOT NULL,
    raw_json TEXT,
    rejected_at TEXT NOT NULL
);
