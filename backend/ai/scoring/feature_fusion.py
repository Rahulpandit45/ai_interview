"""
feature_fusion.py
Multimodal Feature Extraction and Fusion.

Assembles 10-dimensional structured feature vector combining:
1. TEXT MODALITY:
   - response_relevance
   - technical_depth
   - speech_fluency_wpm
2. AUDIO MODALITY:
   - audio_clarity_score
   - pause_ratio
3. VIDEO MODALITY:
   - eye_contact_pct
   - head_stability_score
   - smile_frequency_ratio
   - face_visibility_pct
4. CONTEXT MODALITY:
   - resume_screening_match
"""

import numpy as np

def build_multimodal_feature_vector(text_features, audio_features, video_features, resume_score=75.0):
    """
    Constructs a 10-dimensional feature vector for the AI scoring engine.
    """
    # 1. Text
    relevance = float(text_features.get("relevance_score", 75.0))
    tech_depth = float(text_features.get("technical_score", 75.0))
    wpm = float(audio_features.get("wpm", 120.0))
    if wpm <= 0:
        wpm = 115.0

    # 2. Audio
    clarity = 85.0 if audio_features.get("word_count", 0) > 10 else 70.0
    duration = float(audio_features.get("duration_seconds", 15.0))
    word_count = int(audio_features.get("word_count", 20))
    pause_ratio = max(0.05, min(0.45, 1.0 - min(1.0, (word_count * 0.4) / max(1.0, duration))))

    # 3. Video
    eye_contact = float(video_features.get("eye_contact_percentage", 80.0))
    head_stability = float(video_features.get("head_stability_score", 82.0))
    smile_ratio = float(video_features.get("smile_frequency_ratio", 0.30))
    face_visibility = float(video_features.get("face_visibility_pct", 90.0))

    # 4. Context
    resume_match = float(resume_score or 75.0)

    feature_vector = np.array([
        relevance,
        tech_depth,
        wpm,
        clarity,
        pause_ratio,
        eye_contact,
        head_stability,
        smile_ratio,
        face_visibility,
        resume_match
    ], dtype=np.float32)

    return feature_vector, {
        "text_relevance": relevance,
        "text_technical_depth": tech_depth,
        "speech_fluency_wpm": wpm,
        "audio_clarity": clarity,
        "pause_ratio": pause_ratio,
        "eye_contact_pct": eye_contact,
        "head_stability": head_stability,
        "smile_ratio": smile_ratio,
        "face_visibility_pct": face_visibility,
        "resume_screening_match": resume_match
    }
