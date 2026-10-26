import json
from datetime import datetime
from app.extensions import db


class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(120), nullable=False)
    topic = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    strengths = db.Column(db.Text, nullable=True)  # JSON list
    improvements = db.Column(db.Text, nullable=True)  # JSON list
    feedback_source = db.Column(db.String(20), nullable=False, default="rule_based")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "question": self.question,
            "answer": self.answer,
            "score": self.score,
            "strengths": json.loads(self.strengths or "[]"),
            "improvements": json.loads(self.improvements or "[]"),
            "feedback_source": self.feedback_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
