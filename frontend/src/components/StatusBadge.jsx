const STATUS_CLASS = {
  Saved: "badge-saved",
  Applied: "badge-applied",
  Assessment: "badge-assessment",
  Interview: "badge-interview",
  Offer: "badge-offer",
  Rejected: "badge-rejected",
};

export default function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_CLASS[status] || "badge-saved"}`}>{status}</span>;
}
