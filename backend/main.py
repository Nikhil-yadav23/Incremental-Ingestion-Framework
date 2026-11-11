
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import (
    get_connection,
    initialize_database
)
from app.pipeline import run_pipeline


app = FastAPI(
    title="Incremental Data Ingestion Framework",
    description="Watermark-based data ingestion with idempotency and recovery.",
    version="1.0.0"
)

# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": "Incremental Data Ingestion Framework"
    }


@app.post("/api/run")
def start_pipeline():
    return run_pipeline()


@app.get("/api/metrics")
def get_metrics():
    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT
                COUNT(*) AS total_runs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                    AS successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)
                    AS failed_runs,
                COALESCE(SUM(rows_read), 0) AS rows_read,
                COALESCE(SUM(inserted), 0) AS inserted,
                COALESCE(SUM(updated), 0) AS updated,
                COALESCE(SUM(deleted), 0) AS deleted,
                COALESCE(SUM(rejected), 0) AS rejected
            FROM pipeline_runs
            """
        ).fetchone()

        return dict(result)

    finally:
        connection.close()


@app.get("/api/records")
def get_records():
    connection = get_connection()

    try:
        records = connection.execute(
            """
            SELECT * FROM target_records
            ORDER BY updated_at DESC
            """
        ).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()


@app.get("/api/rejections")
def get_rejections():
    connection = get_connection()

    try:
        records = connection.execute(
            """
            SELECT * FROM rejected_records
            ORDER BY reject_id DESC
            """
        ).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()


@app.get("/api/runs")
def get_runs():
    connection = get_connection()

    try:
        records = connection.execute(
            """
            SELECT * FROM pipeline_runs
            ORDER BY started_at DESC
            """
        ).fetchall()

        return [dict(record) for record in records]

    finally:
        connection.close()
