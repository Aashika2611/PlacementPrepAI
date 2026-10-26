import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 12,
      textAlign: "center",
      padding: 24,
    }}>
      <div style={{ fontFamily: "var(--font-display)", fontSize: 56, fontWeight: 700, color: "var(--color-primary)" }}>404</div>
      <h1 style={{ fontSize: 20 }}>Page not found</h1>
      <p style={{ color: "var(--color-ink-muted)", maxWidth: 360 }}>
        The page you're looking for doesn't exist or may have been moved.
      </p>
      <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: 8 }}>
        Back to dashboard
      </Link>
    </div>
  );
}
