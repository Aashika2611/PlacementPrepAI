from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models import Application, ResumeAnalysis, InterviewSession, VALID_STATUSES

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    user_id = int(get_jwt_identity())

    latest_resume = (
        ResumeAnalysis.query.filter_by(user_id=user_id)
        .order_by(ResumeAnalysis.created_at.desc())
        .first()
    )

    total_applications = Application.query.filter_by(user_id=user_id).count()

    status_counts_query = (
        db.session.query(Application.status, func.count(Application.id))
        .filter_by(user_id=user_id)
        .group_by(Application.status)
        .all()
    )
    status_counts = {status: 0 for status in VALID_STATUSES}
    for status, count in status_counts_query:
        status_counts[status] = count

    interview_session_count = InterviewSession.query.filter_by(user_id=user_id).count()

    recent_applications = (
        Application.query.filter_by(user_id=user_id)
        .order_by(Application.created_at.desc())
        .limit(5)
        .all()
    )

    avg_interview_score = (
        db.session.query(func.avg(InterviewSession.score))
        .filter(InterviewSession.user_id == user_id, InterviewSession.score.isnot(None))
        .scalar()
    )

    return jsonify({
        "latest_resume_score": latest_resume.score if latest_resume else None,
        "total_applications": total_applications,
        "applications_by_status": status_counts,
        "interview_sessions_count": interview_session_count,
        "average_interview_score": round(avg_interview_score, 1) if avg_interview_score else None,
        "recent_applications": [a.to_dict() for a in recent_applications],
    }), 200
