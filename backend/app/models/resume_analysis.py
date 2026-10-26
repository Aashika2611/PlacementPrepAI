import json
from datetime import datetime
from app.extensions import db


class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    skills_detected = db.Column(db.Text, nullable=True)  # JSON list
    strengths = db.Column(db.Text, nullable=True)  # JSON list
    weaknesses = db.Column(db.Text, nullable=True)  # JSON list
    suggestions = db.Column(db.Text, nullable=True)  # JSON list
    sections_detected = db.Column(db.Text, nullable=True)  # JSON list
    analysis_source = db.Column(db.String(20), nullable=False, default="rule_based")  # "ai" or "rule_based"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "score": self.score,
            "skills_detected": json.loads(self.skills_detected or "[]"),
            "strengths": json.loads(self.strengths or "[]"),
            "weaknesses": json.loads(self.weaknesses or "[]"),
            "suggestions": json.loads(self.suggestions or "[]"),
            "sections_detected": json.loads(self.sections_detected or "[]"),
            "analysis_source": self.analysis_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
