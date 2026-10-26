import { useEffect, useRef, useState } from "react";
import { api } from "../services/api";
import PageHeader from "../components/PageHeader";
import ScoreRing from "../components/ScoreRing";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import "./ResumeAnalyzer.css";

function ListBlock({ title, items, tone }) {
  if (!items || items.length === 0) return null;
  return (
    <div className={`resume-list-block resume-list-${tone}`}>
      <h4>{title}</h4>
      <ul>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function ResumeAnalyzer() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [aiEnabled, setAiEnabled] = useState(null);
  const fileInputRef = useRef(null);

  const loadHistory = () => {
    setHistoryLoading(true);
    api
      .get("/resume/history")
      .then((data) => setHistory(data.analyses))
      .catch(() => {})
      .finally(() => setHistoryLoading(false));
  };

  useEffect(() => {
    loadHistory();
    fetch((import.meta.env.VITE_API_URL || "http://localhost:5000/api") + "/health")
      .then((r) => r.json())
      .then((d) => setAiEnabled(d.ai_enabled))
      .catch(() => setAiEnabled(null));
  }, []);

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    setError("");
    if (selected && selected.type !== "application/pdf") {
      setError("Please select a PDF file.");
      setFile(null);
      return;
    }
    setFile(selected || null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please choose a PDF resume first.");
      return;
    }
    setError("");
    setAnalyzing(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("resume", file);
      const data = await api.postForm("/resume/analyze", formData);
      setResult(data.analysis);
      loadHistory();
      if (fileInputRef.current) fileInputRef.current.value = "";
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Resume Analyzer"
        subtitle="Upload a PDF resume to get an application-generated score and improvement suggestions."
      />

      {aiEnabled === false && (
        <div className="banner banner-info" style={{ marginBottom: 20 }}>
          No AI API key is configured on the backend, so analysis uses PlacementPrep AI's built-in
          rule-based engine instead of an LLM. Results are still real, just not AI-generated.
        </div>
      )}

      <div className="card resume-upload-card">
        <form onSubmit={handleAnalyze}>
          <div className="resume-dropzone">
            <input
              ref={fileInputRef}
              id="resume-file"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
            />
            <label htmlFor="resume-file" className="resume-dropzone-label">
              <svg width="26" height="26" viewBox="0 0 20 20" fill="none">
                <path d="M5 2.5h6.5L15 6v11a1 1 0 01-1 1H5a1 1 0 01-1-1V3.5a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
                <path d="M11 2.5V6h4" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
              </svg>
              <span>{file ? file.name : "Click to choose a PDF resume (max 5MB)"}</span>
            </label>
          </div>
          {error && <div className="banner banner-error" style={{ marginTop: 14 }}>{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={analyzing} style={{ marginTop: 16 }}>
            {analyzing ? "Analyzing…" : "Analyze resume"}
          </button>
        </form>
      </div>

      {analyzing && <LoadingSpinner label="Reading and analyzing your resume…" />}

      {result && (
        <div className="card resume-result-card">
          <div className="resume-result-header">
            <ScoreRing score={result.score} size={110} label="Resume score / 100" />
            <div className="resume-result-meta">
              <div className="resume-result-filename">{result.filename}</div>
              <div className="resume-result-source">
                {result.analysis_source === "ai" ? "AI-assisted analysis" : "Rule-based analysis"}
              </div>
              <div className="resume-result-note">
                This is an application-generated score, not an official ATS score.
              </div>
            </div>
          </div>

          <div className="resume-result-sections">
            <ListBlock title="Strengths" items={result.strengths} tone="success" />
            <ListBlock title="Weaknesses" items={result.weaknesses} tone="danger" />
            <ListBlock title="Suggestions" items={result.suggestions} tone="primary" />
          </div>

          {result.skills_detected.length > 0 && (
            <div className="resume-skills">
              <h4>Skills Detected</h4>
              <div className="resume-skills-tags">
                {result.skills_detected.map((s, i) => (
                  <span key={i} className="resume-skill-tag">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="resume-history-section">
        <h2>Previous Analyses</h2>
        {historyLoading ? (
          <LoadingSpinner label="Loading history…" />
        ) : history.length === 0 ? (
          <div className="card">
            <EmptyState title="No previous analyses" description="Your resume analysis history will appear here." />
          </div>
        ) : (
          <div className="resume-history-list">
            {history.map((h) => (
              <div key={h.id} className="card resume-history-item">
                <ScoreRing score={h.score} size={56} strokeWidth={5} />
                <div className="resume-history-info">
                  <div className="resume-history-filename">{h.filename}</div>
                  <div className="resume-history-date">
                    {new Date(h.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                    {" · "}{h.analysis_source === "ai" ? "AI-assisted" : "Rule-based"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
