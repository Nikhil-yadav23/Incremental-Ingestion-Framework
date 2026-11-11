# Setup and Execution Guide

## 1. Project Requirements

Install the following before running the application:

- Python 3.10 or later
- Node.js and npm
- Git
- Visual Studio Code (recommended)

## 2. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/Nikhil-yadav23/Incremental-Ingestion-Framework.git
cd Incremental-Ingestion-Framework
```

## 3. Backend Setup

Open a terminal in the project root and navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment:

**Windows:**
```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 4. Generate Sample Data

From the `backend` directory, run:

```bash
python scripts/generator.py
```

This generates reproducible sample events for testing the ingestion pipeline.

## 5. Start the Backend

From the `backend` directory, run:

```bash
python -m uvicorn main:app --reload
```

The backend API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

The database is initialized automatically when the backend starts.

## 6. Frontend Setup

Open a second terminal and navigate to the frontend:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the dashboard at:

`http://localhost:5173`

On Windows PowerShell, use `npm.cmd` instead of `npm` if script execution is blocked.

## 7. Run the Pipeline

1. Open the dashboard.
2. Click **Run Pipeline**.
3. Review inserted, updated, deleted, and rejected record counts.
4. Inspect the target records and run history.
5. Run the pipeline again to verify that previously processed events do not create duplicate target records.

## 8. Available API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check backend health |
| POST | `/api/run` | Execute the ingestion pipeline |
| GET | `/api/metrics` | View pipeline metrics |
| GET | `/api/records` | View target records |
| GET | `/api/rejections` | View rejected records |
| GET | `/api/runs` | View execution history |

## 9. Run Automated Tests

Open a terminal in the `backend` directory and run:

```bash
python -m pytest -v
```

Expected result for the current test suite:

`12 passed`

## 10. Troubleshooting

- **Backend does not start:** Check that dependencies are installed and the backend virtual environment is activated.
- **Frontend cannot connect to backend:** Confirm that the backend is running on port 8000.
- **Dashboard does not open:** Confirm that the frontend development server is running on port 5173.
- **Database issues:** Stop the backend and check the database path and schema file at `database/schema.sql`.
- **Port already in use:** Stop the process using the port or configure a different port.

## 11. Stopping the Application

Press `Ctrl + C` in each terminal running the frontend and backend.

## 12. Reproducibility

The project uses a local JSONL input file and SQLite database. The sample generator, setup instructions, API endpoints, and automated tests provide a reproducible local evaluation workflow.