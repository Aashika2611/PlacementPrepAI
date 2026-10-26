import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import ScoreRing from "../components/ScoreRing";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import "./Dashboard.css";

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    api
      .get("/dashboard/summary")
      .then((data) => active && setSummary(data))
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  if (loading) return <LoadingSpinner label="Loading your dashboard…" />;
  if (error) return <div className="banner banner-error">{error}</div>;

  const hasActivity = summary.total_applications > 0 || summary.latest_resume_score !== null || summary.interview_sessions_count > 0;

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name?.split(" ")[0] || "there"}`}
        subtitle="Here's where your placement prep stands right now."
      />

      <div className="dashboard-grid">
        <StatCard
          label="Total Applications"
          value={summary.total_applications}
          sublabel="Across all statuses"
          accent="primary"
        />
        <StatCard
          label="Interview Sessions"
          value={summary.interview_sessions_count}
          sublabel={summary.average_interview_score ? `Avg score: ${summary.average_interview_score}` : "No sessions yet"}
          accent="neutral"
        />
        <StatCard
          label="Offers"
          value={summary.applications_by_status?.Offer ?? 0}
          sublabel="Keep going!"
          accent="success"
        />
        <StatCard
          label="In Progress"
          value={(summary.applications_by_status?.Applied ?? 0) + (summary.applications_by_status?.Assessment ?? 0) + (summary.applications_by_status?.Interview ?? 0)}
          sublabel="Applied, Assessment or Interview"
          accent="warning"
        />
      </div>

      {!hasActivity ? (
        <div className="card">
          <EmptyState
            title="No activity yet"
            description="Upload a resume, start an interview session, or track your first application to see your stats here."
            action={
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "center" }}>
                <Link to="/resume-analyzer" className="btn btn-primary">Analyze resume</Link>
                <Link to="/applications" className="btn btn-secondary">Add application</Link>
              </div>
            }
          />
        </div>
      ) : (
        <div className="dashboard-lower">
          <div className="card dashboard-panel">
            <div className="dashboard-panel-header">
              <h2>Recent Applications</h2>
              <Link to="/applications">View all</Link>
            </div>
            {summary.recent_applications.length === 0 ? (
              <EmptyState title="No applications tracked yet" description="Add your first application to see it here." />
            ) : (
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Role</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.recent_applications.map((a) => (
                    <tr key={a.id}>
                      <td>{a.company}</td>
                      <td>{a.job_title}</td>
                      <td><StatusBadge status={a.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="card dashboard-panel dashboard-panel-score">
            <h2>Latest Resume Score</h2>
            {summary.latest_resume_score !== null ? (
              <>
                <ScoreRing score={summary.latest_resume_score} size={120} label="out of 100" />
                <Link to="/resume-analyzer" className="btn btn-secondary" style={{ marginTop: 18 }}>
                  Re-analyze resume
                </Link>
              </>
            ) : (
              <EmptyState
                title="No resume analyzed yet"
                description="Upload your resume to get a score and tailored suggestions."
                action={<Link to="/resume-analyzer" className="btn btn-primary">Analyze resume</Link>}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
