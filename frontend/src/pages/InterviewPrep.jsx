import { useEffect, useState } from "react";
import { api } from "../services/api";
import PageHeader from "../components/PageHeader";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import "./InterviewPrep.css";

export default function InterviewPrep() {
  const [options, setOptions] = useState(null);
  const [role, setRole] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("");

  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState("");
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    api.get("/interview/options").then((data) => {
      setOptions(data);
      setRole(data.roles[0]);
      setTopic(data.topics[0]);
      setDifficulty(data.difficulties[0]);
    });
    loadHistory();
  }, []);

  const loadHistory = () => {
    setHistoryLoading(true);
    api
      .get("/interview/history")
      .then((data) => setHistory(data.sessions))
      .catch(() => {})
      .finally(() => setHistoryLoading(false));
  };

  const handleGetQuestion = async () => {
    setError("");
    setLoadingQuestion(true);
    setSession(null);
    setAnswer("");
    try {
      const data = await api.post("/interview/question", { role, topic, difficulty });
      setSession(data.session);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (!answer.trim()) {
      setError("Please write an answer before submitting.");
      return;
    }
    setError("");
    setSubmittingAnswer(true);
    try {
      const data = await api.post(`/interview/${session.id}/answer`, { answer });
      setSession(data.session);
      loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingAnswer(false);
    }
  };

  if (!options) return <LoadingSpinner label="Loading interview prep…" />;

  return (
    <div>
      <PageHeader
        title="Interview Preparation"
        subtitle="Pick a role, topic, and difficulty, then practice answering real questions."
      />

      <div className="card interview-setup-card">
        <div className="interview-setup-grid">
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Job Role</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {options.roles.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Topic</label>
            <select value={topic} onChange={(e) => setTopic(e.target.value)}>
              {options.topics.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Difficulty</label>
            <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              {options.difficulties.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>
        <button className="btn btn-primary" onClick={handleGetQuestion} disabled={loadingQuestion} style={{ marginTop: 18 }}>
          {loadingQuestion ? "Generating question…" : "Get a question"}
        </button>
      </div>

      {error && <div className="banner banner-error" style={{ margin: "16px 0" }}>{error}</div>}

      {session && (
        <div className="card interview-question-card">
          <div className="interview-question-tags">
            <span className="badge badge-applied">{session.role}</span>
            <span className="badge badge-saved">{session.topic}</span>
            <span className="badge badge-assessment">{session.difficulty}</span>
          </div>
          <p className="interview-question-text">{session.question}</p>

          {session.score === null || session.score === undefined ? (
            <form onSubmit={handleSubmitAnswer}>
              <div className="field">
                <label>Your answer</label>
                <textarea
                  rows={6}
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer here…"
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={submittingAnswer}>
                {submittingAnswer ? "Getting feedback…" : "Submit answer"}
              </button>
            </form>
          ) : (
            <div className="interview-feedback">
              <div className="interview-feedback-header">
                <div className={"interview-score mono " + (session.score >= 70 ? "score-good" : session.score >= 40 ? "score-mid" : "score-low")}>
                  {session.score}
                  <span>/100</span>
                </div>
                <div className="interview-feedback-source">
                  {session.feedback_source === "ai" ? "AI-assisted feedback" : "Rule-based feedback"}
                </div>
              </div>

              <div className="interview-answer-echo">
                <h4>Your answer</h4>
                <p>{session.answer}</p>
              </div>

              <div className="interview-feedback-lists">
                <div>
                  <h4 className="feedback-good">Strengths</h4>
                  <ul>{session.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
                <div>
                  <h4 className="feedback-improve">Improvements</h4>
                  <ul>{session.improvements.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              </div>

              <button className="btn btn-secondary" onClick={handleGetQuestion} style={{ marginTop: 8 }}>
                Try another question
              </button>
            </div>
          )}
        </div>
      )}

      <div className="interview-history-section">
        <button className="btn btn-ghost interview-history-toggle" onClick={() => setShowHistory((s) => !s)}>
          {showHistory ? "Hide" : "Show"} session history ({history.length})
        </button>
        {showHistory && (
          historyLoading ? (
            <LoadingSpinner label="Loading history…" />
          ) : history.length === 0 ? (
            <div className="card"><EmptyState title="No sessions yet" description="Sessions you complete will show up here." /></div>
          ) : (
            <div className="interview-history-list">
              {history.map((s) => (
                <div key={s.id} className="card interview-history-item">
                  <div className="interview-history-item-top">
                    <div>
                      <span className="badge badge-saved">{s.topic}</span>{" "}
                      <span className="badge badge-assessment">{s.difficulty}</span>
                    </div>
                    {s.score !== null && <span className="mono interview-history-score">{s.score}/100</span>}
                  </div>
                  <p className="interview-history-question">{s.question}</p>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
