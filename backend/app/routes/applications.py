from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Application, VALID_STATUSES
from app.utils.validators import require_fields

applications_bp = Blueprint("applications", __name__, url_prefix="/api/applications")


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


@applications_bp.route("", methods=["GET"])
@jwt_required()
def list_applications():
    user_id = int(get_jwt_identity())
    status = request.args.get("status")

    query = Application.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)

    applications = query.order_by(Application.created_at.desc()).all()
    return jsonify({"applications": [a.to_dict() for a in applications]}), 200


@applications_bp.route("", methods=["POST"])
@jwt_required()
def create_application():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["company", "job_title"])
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    status = data.get("status", "Saved")
    if status not in VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400

    application = Application(
        user_id=user_id,
        company=data["company"].strip(),
        job_title=data["job_title"].strip(),
        application_date=_parse_date(data.get("application_date")),
        status=status,
        job_url=(data.get("job_url") or "").strip() or None,
        notes=(data.get("notes") or "").strip() or None,
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({"application": application.to_dict()}), 201


@applications_bp.route("/<int:app_id>", methods=["GET"])
@jwt_required()
def get_application(app_id):
    user_id = int(get_jwt_identity())
    application = Application.query.filter_by(id=app_id, user_id=user_id).first()
    if not application:
        return jsonify({"error": "Application not found."}), 404
    return jsonify({"application": application.to_dict()}), 200


@applications_bp.route("/<int:app_id>", methods=["PUT"])
@jwt_required()
def update_application(app_id):
    user_id = int(get_jwt_identity())
    application = Application.query.filter_by(id=app_id, user_id=user_id).first()
    if not application:
        return jsonify({"error": "Application not found."}), 404

    data = request.get_json(silent=True) or {}

    if "company" in data:
        if not data["company"].strip():
            return jsonify({"error": "Company cannot be empty."}), 400
        application.company = data["company"].strip()

    if "job_title" in data:
        if not data["job_title"].strip():
            return jsonify({"error": "Job title cannot be empty."}), 400
        application.job_title = data["job_title"].strip()

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400
        application.status = data["status"]

    if "application_date" in data:
        application.application_date = _parse_date(data.get("application_date"))

    if "job_url" in data:
        application.job_url = (data.get("job_url") or "").strip() or None

    if "notes" in data:
        application.notes = (data.get("notes") or "").strip() or None

    db.session.commit()
    return jsonify({"application": application.to_dict()}), 200


@applications_bp.route("/<int:app_id>", methods=["DELETE"])
@jwt_required()
def delete_application(app_id):
    user_id = int(get_jwt_identity())
    application = Application.query.filter_by(id=app_id, user_id=user_id).first()
    if not application:
        return jsonify({"error": "Application not found."}), 404

    db.session.delete(application)
    db.session.commit()
    return jsonify({"message": "Application deleted."}), 200
