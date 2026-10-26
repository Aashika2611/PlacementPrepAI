import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import PageHeader from "../components/PageHeader";
import "./Profile.css";

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", target_role: "", skills: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        name: user.name || "",
        email: user.email || "",
        target_role: user.target_role || "",
        skills: (user.skills || []).join(", "),
      });
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);
    try {
      const data = await api.put("/profile", {
        name: form.name.trim(),
        email: form.email.trim(),
        target_role: form.target_role.trim(),
        skills: form.skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      updateUser(data.user);
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <PageHeader title="Profile" subtitle="Update your personal details and target role." />

      <div className="card profile-card">
        {error && <div className="banner banner-error" style={{ marginBottom: 16 }}>{error}</div>}
        {success && <div className="banner banner-info" style={{ marginBottom: 16 }}>{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="profile-form-grid">
            <div className="field">
              <label>Full name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="field">
              <label>Email</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
          </div>

          <div className="field">
            <label>Target role</label>
            <input
              value={form.target_role}
              onChange={(e) => setForm({ ...form, target_role: e.target.value })}
              placeholder="e.g. Backend Developer"
            />
          </div>

          <div className="field">
            <label>Skills (comma-separated)</label>
            <textarea
              rows={3}
              value={form.skills}
              onChange={(e) => setForm({ ...form, skills: e.target.value })}
              placeholder="Python, React, SQL, Git"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : "Save changes"}
          </button>
        </form>
      </div>
    </div>
  );
}
