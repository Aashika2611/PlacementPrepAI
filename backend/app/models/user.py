from datetime import datetime
import bcrypt
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    target_role = db.Column(db.String(120), nullable=True)
    skills = db.Column(db.Text, nullable=True)  # comma-separated skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship(
        "Application", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    resume_analyses = db.relationship(
        "ResumeAnalysis", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    interview_sessions = db.relationship(
        "InterviewSession", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = bcrypt.hashpw(
            raw_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.checkpw(
            raw_password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "target_role": self.target_role,
            "skills": [s.strip() for s in self.skills.split(",")] if self.skills else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
