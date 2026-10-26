import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "grid" },
  { to: "/resume-analyzer", label: "Resume Analyzer", icon: "file" },
  { to: "/interview-prep", label: "Interview Prep", icon: "message" },
  { to: "/applications", label: "Applications", icon: "briefcase" },
  { to: "/profile", label: "Profile", icon: "user" },
];

const ICONS = {
  grid: (
    <svg viewBox="0 0 20 20" fill="none"><rect x="2.5" y="2.5" width="6" height="6" rx="1.3" stroke="currentColor" strokeWidth="1.5"/><rect x="11.5" y="2.5" width="6" height="6" rx="1.3" stroke="currentColor" strokeWidth="1.5"/><rect x="2.5" y="11.5" width="6" height="6" rx="1.3" stroke="currentColor" strokeWidth="1.5"/><rect x="11.5" y="11.5" width="6" height="6" rx="1.3" stroke="currentColor" strokeWidth="1.5"/></svg>
  ),
  file: (
    <svg viewBox="0 0 20 20" fill="none"><path d="M5 2.5h6.5L15 6v11a1 1 0 01-1 1H5a1 1 0 01-1-1V3.5a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M11 2.5V6h4" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
  ),
  message: (
    <svg viewBox="0 0 20 20" fill="none"><path d="M3 4.5A1.5 1.5 0 014.5 3h11A1.5 1.5 0 0117 4.5v7A1.5 1.5 0 0115.5 13H8l-3.5 3.5V13H4.5A1.5 1.5 0 013 11.5v-7z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
  ),
  briefcase: (
    <svg viewBox="0 0 20 20" fill="none"><rect x="2.5" y="6" width="15" height="10" rx="1.5" stroke="currentColor" strokeWidth="1.5"/><path d="M7 6V4.5A1.5 1.5 0 018.5 3h3A1.5 1.5 0 0113 4.5V6" stroke="currentColor" strokeWidth="1.5"/></svg>
  ),
  user: (
    <svg viewBox="0 0 20 20" fill="none"><circle cx="10" cy="6.5" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M3.5 17c.9-3.3 3.7-5 6.5-5s5.6 1.7 6.5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  ),
};

export default function Sidebar({ onNavigate }) {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-brand-mark">PP</span>
        <span className="sidebar-brand-name">PlacementPrep<span className="accent">.AI</span></span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
          >
            <span className="sidebar-icon">{ICONS[item.icon]}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">{user?.name?.[0]?.toUpperCase() || "?"}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.name}</div>
            <div className="sidebar-user-email">{user?.email}</div>
          </div>
        </div>
        <button className="btn btn-ghost sidebar-logout" onClick={logout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
