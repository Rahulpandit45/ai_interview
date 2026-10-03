import os
import pickle
import numpy as np
from backend.config import Config

_scoring_model = None

def get_scoring_model():
    global _scoring_model
    if _scoring_model is None:
        model_path = Config.SCORING_MODEL_PATH
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    payload = pickle.load(f)
                    _scoring_model = payload.get("model")
                    print("[AI Scoring] Multimodal Random Forest Model loaded successfully.")
            except Exception as e:
                print(f"[AI Scoring Warning] Could not load model: {e}")
                _scoring_model = None
    return _scoring_model

def calculate_ai_assessment_scores(feature_vector, metrics_dict):
    """
    Feeds the 10-dimensional multimodal feature vector to the trained Random Forest model.
    Falls back to analytical weighted rubric if model artifact is reloading.
    """
    model = get_scoring_model()
    
    if model is not None:
        try:
            X_input = feature_vector.reshape(1, -1)
            preds = model.predict(X_input)[0]
            comm_score = float(np.clip(preds[0], 0, 100))
            tech_score = float(np.clip(preds[1], 0, 100))
            conf_score = float(np.clip(preds[2], 0, 100))
            overall_score = float(np.clip(preds[3], 0, 100))
        except Exception as e:
            print(f"[AI Scoring Error] Prediction failed: {e}. Using weighted heuristic.")
            comm_score, tech_score, conf_score, overall_score = _calculate_heuristic_scores(metrics_dict)
    else:
        comm_score, tech_score, conf_score, overall_score = _calculate_heuristic_scores(metrics_dict)

    # Generate Strengths and Areas for Improvement
    strengths, weaknesses, feedback = generate_personalized_feedback(
        comm_score, tech_score, conf_score, overall_score, metrics_dict
    )

    return {
        "communication_score": round(comm_score, 1),
        "technical_score": round(tech_score, 1),
        "confidence_score": round(conf_score, 1),
        "overall_score": round(overall_score, 1),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback
    }

def _calculate_heuristic_scores(m):
    comm = (0.35 * m.get("audio_clarity", 80) + 
            0.25 * min(100, (m.get("speech_fluency_wpm", 120) / 140.0) * 100) + 
            0.20 * m.get("eye_contact_pct", 80) + 
            0.20 * m.get("text_relevance", 75))
            
    tech = (0.50 * m.get("text_technical_depth", 75) + 
            0.30 * m.get("text_relevance", 75) + 
            0.20 * m.get("resume_screening_match", 75))
            
    conf = (0.35 * m.get("eye_contact_pct", 80) + 
            0.30 * m.get("head_stability", 80) + 
            0.20 * (1.0 - m.get("pause_ratio", 0.15)) * 100 + 
            0.15 * m.get("audio_clarity", 80))
            
    overall = (0.35 * tech + 0.30 * comm + 0.25 * conf + 0.10 * (m.get("face_visibility_pct", 90)))
    return comm, tech, conf, overall

def generate_personalized_feedback(comm, tech, conf, overall, m):
    strengths = []
    weaknesses = []
    
    # Analyze strengths
    if tech >= 78.0:
        strengths.append("Strong technical knowledge and domain vocabulary precision.")
    if comm >= 80.0:
        strengths.append("Clear verbal communication with steady, natural speaking cadence.")
    if conf >= 80.0:
        strengths.append("Confident posture, consistent eye contact, and attentive engagement.")
    if m.get("eye_contact_pct", 0) >= 80.0:
        strengths.append("Maintained consistent direct eye contact with the camera.")
    if not strengths:
        strengths.append("Good foundational understanding of the core interview subject matter.")
        strengths.append("Clear enthusiasm and willingness to address complex engineering topics.")

    # Analyze areas for improvement
    if tech < 75.0:
        weaknesses.append("Deepen technical explanations with specific architectural trade-offs.")
    if m.get("speech_fluency_wpm", 120) < 95.0:
        weaknesses.append("Work on speech fluency and reducing prolonged hesitation pauses.")
    elif m.get("speech_fluency_wpm", 120) > 155.0:
        weaknesses.append("Pace your speaking rate slightly to ensure clarity when presenting complex concepts.")
    if m.get("eye_contact_pct", 0) < 70.0:
        weaknesses.append("Increase camera eye contact to project greater engagement and confidence.")
    if m.get("head_stability", 0) < 70.0:
        weaknesses.append("Maintain a centered, calm physical posture during responses.")
    if not weaknesses:
        weaknesses.append("Provide even more quantitative metrics and architectural edge cases.")
        weaknesses.append("Continue refining concise STAR-method storytelling for behavioral questions.")

    grade = "Outstanding" if overall >= 88 else ("Good" if overall >= 75 else ("Satisfactory" if overall >= 60 else "Needs Improvement"))
    feedback = (
        f"Candidate delivered a {grade.lower()} overall interview performance ({overall:.1f}/100). "
        f"Demonstrated a communication score of {comm:.1f}%, technical knowledge of {tech:.1f}%, "
        f"and confidence metric of {conf:.1f}%. Eye contact consistency was measured at {m.get('eye_contact_pct', 0):.1f}%."
    )
    
    return strengths, weaknesses, feedback
