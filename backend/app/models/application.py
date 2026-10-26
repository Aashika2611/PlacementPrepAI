from datetime import datetime
from app.extensions import db

VALID_STATUSES = ["Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"]


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company = db.Column(db.String(150), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    application_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Saved")
    job_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "job_title": self.job_title,
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "status": self.status,
            "job_url": self.job_url,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
