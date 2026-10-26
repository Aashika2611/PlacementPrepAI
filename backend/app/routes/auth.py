from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User
from app.utils.validators import is_valid_email, is_valid_password, require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["name", "email", "password"])
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if not is_valid_email(email):
        return jsonify({"error": "Please provide a valid email address."}), 400

    if not is_valid_password(password):
        return jsonify({"error": "Password must be at least 8 characters and include a letter and a number."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200
