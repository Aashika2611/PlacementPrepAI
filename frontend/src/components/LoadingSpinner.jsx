import "./LoadingSpinner.css";

export default function LoadingSpinner({ label = "Loading…", size = 22 }) {
  return (
    <div className="loading-spinner-wrap">
      <span
        className="loading-spinner"
        style={{ width: size, height: size, borderWidth: Math.max(2, size / 10) }}
      />
      {label && <span className="loading-spinner-label">{label}</span>}
    </div>
  );
}
