"""
qa_routes.py
Flask Blueprint for IT Q&A endpoint: POST /api/qa/ask.
Integrates the QAService directly into the existing Flask backend (Port 5000).
"""

from flask import Blueprint, request, jsonify
from backend.services.qa_service import QAService

qa_bp = Blueprint("qa", __name__, url_prefix="/api/qa")


@qa_bp.route("/ask", methods=["POST"])
def ask_question():
    """
    POST /api/qa/ask
    Input:
        {"question": "What is Python?"}
    Output:
        {"question": "What is Python?", "answer": "Python is a high-level programming language used to create software."}
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not question or not question.strip():
        return jsonify({"error": "The 'question' field is required."}), 400

    style = data.get("style", "standard")
    result = QAService.answer_question(question, answer_style=style)

    return jsonify({
        "question": result["question"],
        "answer": result["answer"]
    }), 200


@qa_bp.route("/categories", methods=["GET"])
def get_categories():
    import os
    import json
    from backend.config import Config

    json_path = os.path.join(Config.BASE_DIR, "datasets", "it_questions.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cat_counts = {}
        for item in data:
            cat = item.get("category", "General")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        return jsonify({"status": "success", "total_categories": len(cat_counts), "categories": cat_counts}), 200

    return jsonify({"status": "error", "message": "Dataset not found"}), 404
