import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import InterviewSession
from app.services.question_bank import (
    ROLES, TOPICS, DIFFICULTIES, get_random_question, evaluate_answer_rule_based,
)
from app.services import ai_service
from app.utils.validators import require_fields

interview_bp = Blueprint("interview", __name__, url_prefix="/api/interview")


@interview_bp.route("/options", methods=["GET"])
@jwt_required()
def get_options():
    return jsonify({"roles": ROLES, "topics": TOPICS, "difficulties": DIFFICULTIES}), 200


@interview_bp.route("/question", methods=["POST"])
@jwt_required()
def new_question():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["role", "topic", "difficulty"])
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    role, topic, difficulty = data["role"], data["topic"], data["difficulty"]

    if topic not in TOPICS:
        return jsonify({"error": f"Invalid topic. Must be one of: {', '.join(TOPICS)}"}), 400
    if difficulty not in DIFFICULTIES:
        return jsonify({"error": f"Invalid difficulty. Must be one of: {', '.join(DIFFICULTIES)}"}), 400

    question_text = None
    if current_app.config.get("AI_ENABLED"):
        question_text = ai_service.generate_interview_question_with_ai(role, topic, difficulty)

    if not question_text:
        question_text = get_random_question(topic, difficulty)

    session = InterviewSession(
        user_id=user_id,
        role=role,
        topic=topic,
        difficulty=difficulty,
        question=question_text,
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({"session": session.to_dict()}), 201


@interview_bp.route("/<int:session_id>/answer", methods=["POST"])
@jwt_required()
def submit_answer(session_id):
    user_id = int(get_jwt_identity())
    session = InterviewSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"error": "Interview session not found."}), 404

    data = request.get_json(silent=True) or {}
    answer = (data.get("answer") or "").strip()
    if not answer:
        return jsonify({"error": "Answer cannot be empty."}), 400

    feedback = None
    feedback_source = "rule_based"
    if current_app.config.get("AI_ENABLED"):
        ai_feedback = ai_service.evaluate_answer_with_ai(
            session.role, session.topic, session.question, answer
        )
        if ai_feedback:
            feedback = ai_feedback
            feedback_source = "ai"

    if feedback is None:
        feedback = evaluate_answer_rule_based(session.question, answer)

    session.answer = answer
    session.score = int(feedback.get("score", 0))
    session.strengths = json.dumps(feedback.get("strengths", []))
    session.improvements = json.dumps(feedback.get("improvements", []))
    session.feedback_source = feedback_source
    db.session.commit()

    return jsonify({"session": session.to_dict()}), 200


@interview_bp.route("/history", methods=["GET"])
@jwt_required()
def interview_history():
    user_id = int(get_jwt_identity())
    sessions = (
        InterviewSession.query.filter_by(user_id=user_id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    return jsonify({"sessions": [s.to_dict() for s in sessions]}), 200
