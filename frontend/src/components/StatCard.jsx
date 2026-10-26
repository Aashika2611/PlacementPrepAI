import "./StatCard.css";

export default function StatCard({ label, value, sublabel, accent = "primary" }) {
  return (
    <div className="stat-card card">
      <div className={`stat-card-bar stat-card-bar-${accent}`} />
      <div className="stat-card-body">
        <div className="stat-card-label">{label}</div>
        <div className="stat-card-value mono">{value}</div>
        {sublabel && <div className="stat-card-sublabel">{sublabel}</div>}
      </div>
    </div>
  );
}
