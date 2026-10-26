import json
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import ResumeAnalysis
from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from app.services.resume_analyzer import analyze_resume_rule_based
from app.services import ai_service

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")


def _allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_RESUME_EXTENSIONS"]
    )


@resume_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_resume():
    user_id = int(get_jwt_identity())

    if "resume" not in request.files:
        return jsonify({"error": "No resume file was uploaded. Use the 'resume' form field."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported."}), 400

    # Extract text directly from the upload stream (also written to disk for reference)
    try:
        extracted_text = extract_text_from_pdf(file.stream)
    except PDFExtractionError as exc:
        return jsonify({"error": str(exc)}), 422

    # Save a copy of the uploaded file with a unique name
    safe_name = f"{uuid.uuid4().hex}_{file.filename.replace('/', '_')}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
    file.stream.seek(0)
    file.save(upload_path)

    # Try AI analysis first (if configured), fall back to rule-based analysis
    analysis_source = "rule_based"
    result = None
    if current_app.config.get("AI_ENABLED"):
        ai_result = ai_service.analyze_resume_with_ai(extracted_text)
        if ai_result:
            result = ai_result
            analysis_source = "ai"

    if result is None:
        result = analyze_resume_rule_based(extracted_text)

    analysis = ResumeAnalysis(
        user_id=user_id,
        filename=file.filename,
        score=int(result.get("score", 0)),
        skills_detected=json.dumps(result.get("skills_detected", [])),
        strengths=json.dumps(result.get("strengths", [])),
        weaknesses=json.dumps(result.get("weaknesses", [])),
        suggestions=json.dumps(result.get("suggestions", [])),
        sections_detected=json.dumps(result.get("sections_detected", [])),
        analysis_source=analysis_source,
    )
    db.session.add(analysis)
    db.session.commit()

    return jsonify({"analysis": analysis.to_dict()}), 201


@resume_bp.route("/history", methods=["GET"])
@jwt_required()
def resume_history():
    user_id = int(get_jwt_identity())
    analyses = (
        ResumeAnalysis.query.filter_by(user_id=user_id)
        .order_by(ResumeAnalysis.created_at.desc())
        .all()
    )
    return jsonify({"analyses": [a.to_dict() for a in analyses]}), 200


@resume_bp.route("/<int:analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis(analysis_id):
    user_id = int(get_jwt_identity())
    analysis = ResumeAnalysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found."}), 404
    return jsonify({"analysis": analysis.to_dict()}), 200
