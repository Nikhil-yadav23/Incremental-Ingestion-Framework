
import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000/api";

function App() {
  const [metrics, setMetrics] = useState({});
  const [records, setRecords] = useState([]);
  const [rejections, setRejections] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadDashboard() {
    try {
      const [m, r, rejected, runData] = await Promise.all([
        fetch(`${API}/metrics`),
        fetch(`${API}/records`),
        fetch(`${API}/rejections`),
        fetch(`${API}/runs`)
      ]);

      if (![m, r, rejected, runData].every(res => res.ok)) {
        throw new Error("Unable to load dashboard data");
      }

      setMetrics(await m.json());
      setRecords(await r.json());
      setRejections(await rejected.json());
      setRuns(await runData.json());
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function startPipeline() {
    setLoading(true);
    setMessage("Pipeline is running...");

    try {
      const response = await fetch(`${API}/run`, {
        method: "POST"
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Pipeline request failed");
      }

      setMessage(
        result.status === "completed"
          ? `Pipeline completed. Read: ${result.rows_read}, Inserted: ${result.inserted}, Updated: ${result.updated}, Deleted: ${result.deleted}, Rejected: ${result.rejected}`
          : `Pipeline failed: ${result.error || "Unknown error"}`
      );

      await loadDashboard();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const cards = [
    ["Total Runs", metrics.total_runs],
    ["Rows Read", metrics.rows_read],
    ["Inserted", metrics.inserted],
    ["Updated", metrics.updated],
    ["Deleted", metrics.deleted],
    ["Rejected", metrics.rejected],
    ["Successful Runs", metrics.successful_runs],
    ["Failed Runs", metrics.failed_runs]
  ];

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>Incremental Data Ingestion</h1>
          <p>Watermark-based data pipeline monitoring</p>
        </div>

        <button onClick={startPipeline} disabled={loading}>
          {loading ? "Running..." : "Run Pipeline"}
        </button>
      </header>

      {message && <div className="message">{message}</div>}

      <section className="metrics">
        {cards.map(([label, value]) => (
          <div className="metric-card" key={label}>
            <p>{label}</p>
            <h2>{value ?? 0}</h2>
          </div>
        ))}
      </section>

      <section className="panel">
        <h2>Target Records</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Updated At</th>
                <th>Sequence</th>
                <th>Status</th>
                <th>Payload</th>
              </tr>
            </thead>
            <tbody>
              {records.map(record => (
                <tr key={record.record_id}>
                  <td>{record.record_id}</td>
                  <td>{record.updated_at}</td>
                  <td>{record.source_sequence}</td>
                  <td>
                    {record.is_deleted ? "Deleted" : "Active"}
                  </td>
                  <td>
                    {record.payload_json || "-"}
                  </td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr><td colSpan="5">No records available</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <h2>Rejected Records</h2>
        {rejections.length === 0 ? (
          <p>No rejected records.</p>
        ) : (
          rejections.map(item => (
            <div className="rejection" key={item.reject_id}>
              <strong>{item.event_id || "Malformed event"}</strong>
              <span>{item.reason}</span>
            </div>
          ))
        )}
      </section>

      <section className="panel">
        <h2>Pipeline Run History</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Status</th>
                <th>Rows Read</th>
                <th>Rejected</th>
                <th>Started At</th>
              </tr>
            </thead>
            <tbody>
              {runs.map(run => (
                <tr key={run.run_id}>
                  <td>{run.run_id.slice(0, 8)}</td>
                  <td>{run.status}</td>
                  <td>{run.rows_read}</td>
                  <td>{run.rejected}</td>
                  <td>{run.started_at}</td>
                </tr>
              ))}
              {runs.length === 0 && (
                <tr><td colSpan="5">No pipeline runs yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default App;
