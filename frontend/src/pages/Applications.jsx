import { useEffect, useState } from "react";
import { api } from "../services/api";
import PageHeader from "../components/PageHeader";
import LoadingSpinner from "../components/LoadingSpinner";
import EmptyState from "../components/EmptyState";
import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";
import "./Applications.css";

const STATUSES = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"];

const EMPTY_FORM = {
  company: "",
  job_title: "",
  status: "Saved",
  application_date: "",
  job_url: "",
  notes: "",
};

export default function Applications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null); // null = create mode
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const loadApplications = () => {
    setLoading(true);
    const query = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : "";
    api
      .get(`/applications${query}`)
      .then((data) => setApplications(data.applications))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadApplications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const openCreateModal = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setModalOpen(true);
  };

  const openEditModal = (app) => {
    setEditing(app);
    setForm({
      company: app.company,
      job_title: app.job_title,
      status: app.status,
      application_date: app.application_date || "",
      job_url: app.job_url || "",
      notes: app.notes || "",
    });
    setFormError("");
    setModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.company.trim() || !form.job_title.trim()) {
      setFormError("Company and job title are required.");
      return;
    }
    setSaving(true);
    setFormError("");
    try {
      if (editing) {
        await api.put(`/applications/${editing.id}`, form);
      } else {
        await api.post("/applications", form);
      }
      setModalOpen(false);
      loadApplications();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.del(`/applications/${deleteTarget.id}`);
      setDeleteTarget(null);
      loadApplications();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Application Tracker"
        subtitle="Keep track of every company you've applied to, from saved to offer."
        action={<button className="btn btn-primary" onClick={openCreateModal}>Add application</button>}
      />

      <div className="applications-filter-row">
        <button
          className={"filter-chip" + (statusFilter === "" ? " active" : "")}
          onClick={() => setStatusFilter("")}
        >
          All
        </button>
        {STATUSES.map((s) => (
          <button
            key={s}
            className={"filter-chip" + (statusFilter === s ? " active" : "")}
            onClick={() => setStatusFilter(s)}
          >
            {s}
          </button>
        ))}
      </div>

      {error && <div className="banner banner-error" style={{ marginBottom: 16 }}>{error}</div>}

      {loading ? (
        <LoadingSpinner label="Loading applications…" />
      ) : applications.length === 0 ? (
        <div className="card">
          <EmptyState
            title={statusFilter ? `No applications with status "${statusFilter}"` : "No applications yet"}
            description="Add a company you've applied to and track its progress here."
            action={<button className="btn btn-primary" onClick={openCreateModal}>Add application</button>}
          />
        </div>
      ) : (
        <div className="applications-list">
          {applications.map((app) => (
            <div key={app.id} className="card application-card">
              <div className="application-card-main">
                <div>
                  <div className="application-card-title">{app.job_title}</div>
                  <div className="application-card-company">{app.company}</div>
                </div>
                <StatusBadge status={app.status} />
              </div>
              <div className="application-card-meta">
                {app.application_date && <span>Applied: {app.application_date}</span>}
                {app.job_url && (
                  <a href={app.job_url} target="_blank" rel="noreferrer">Job posting ↗</a>
                )}
              </div>
              {app.notes && <p className="application-card-notes">{app.notes}</p>}
              <div className="application-card-actions">
                <button className="btn btn-secondary" onClick={() => openEditModal(app)}>Edit</button>
                <button className="btn btn-danger" onClick={() => setDeleteTarget(app)}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <Modal title={editing ? "Edit Application" : "Add Application"} onClose={() => setModalOpen(false)}>
          {formError && <div className="banner banner-error" style={{ marginBottom: 14 }}>{formError}</div>}
          <form onSubmit={handleSave}>
            <div className="field">
              <label>Company *</label>
              <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required />
            </div>
            <div className="field">
              <label>Job Title *</label>
              <input value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} required />
            </div>
            <div className="field">
              <label>Status</label>
              <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Application Date</label>
              <input type="date" value={form.application_date} onChange={(e) => setForm({ ...form, application_date: e.target.value })} />
            </div>
            <div className="field">
              <label>Job URL</label>
              <input type="url" value={form.job_url} onChange={(e) => setForm({ ...form, job_url: e.target.value })} placeholder="https://…" />
            </div>
            <div className="field">
              <label>Notes</label>
              <textarea rows={3} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </div>
            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Saving…" : editing ? "Save changes" : "Add application"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {deleteTarget && (
        <Modal
          title="Delete application?"
          onClose={() => setDeleteTarget(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setDeleteTarget(null)}>Cancel</button>
              <button className="btn btn-danger" onClick={handleDelete} disabled={deleting}>
                {deleting ? "Deleting…" : "Delete"}
              </button>
            </>
          }
        >
          <p>This will permanently remove your application to <strong>{deleteTarget.company}</strong> ({deleteTarget.job_title}). This cannot be undone.</p>
        </Modal>
      )}
    </div>
  );
}
