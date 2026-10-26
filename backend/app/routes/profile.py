from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User
from app.utils.validators import is_valid_email

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("", methods=["GET"])
@jwt_required()
def get_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200


@profile_bp.route("", methods=["PUT"])
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return jsonify({"error": "Name cannot be empty."}), 400
        user.name = name

    if "email" in data:
        email = (data["email"] or "").strip().lower()
        if not is_valid_email(email):
            return jsonify({"error": "Please provide a valid email address."}), 400
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return jsonify({"error": "This email is already in use."}), 409
        user.email = email

    if "target_role" in data:
        user.target_role = (data["target_role"] or "").strip() or None

    if "skills" in data:
        skills = data["skills"]
        if isinstance(skills, list):
            user.skills = ", ".join(s.strip() for s in skills if s.strip())
        elif isinstance(skills, str):
            user.skills = skills.strip()

    db.session.commit()
    return jsonify({"user": user.to_dict()}), 200
