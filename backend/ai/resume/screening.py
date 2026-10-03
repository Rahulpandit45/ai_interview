import numpy as np

ROLE_REQUIREMENTS = {
    "Software Engineer": {
        "required_skills": ["Python", "Flask", "Sql", "Git", "Data Structures", "Algorithms", "Oop", "Rest Api"],
        "preferred_skills": ["Docker", "Linux", "Javascript", "Mysql", "System Design"],
        "description": "Software engineer responsible for building scalable backend APIs, database models, and maintaining software quality."
    },
    "AI/ML Engineer": {
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "Pytorch", "Tensorflow", "Numpy", "Pandas"],
        "preferred_skills": ["Computer Vision", "Nlp", "Opencv", "Transformers", "Scikit-Learn"],
        "description": "AI and Machine Learning engineer developing deep neural networks, computer vision, speech models, and NLP systems."
    },
    "Full Stack Developer": {
        "required_skills": ["Javascript", "Html", "Css", "React", "Python", "Sql", "Rest Api"],
        "preferred_skills": ["Node.js", "Flask", "Mysql", "Git", "Typescript", "Docker"],
        "description": "Full stack developer designing modern reactive user interfaces and robust server-side APIs."
    },
    "Data Scientist": {
        "required_skills": ["Python", "Pandas", "Numpy", "Scikit-Learn", "Sql", "Machine Learning"],
        "preferred_skills": ["Deep Learning", "Matplotlib", "Statistics", "Data Mining"],
        "description": "Data scientist analyzing complex data, engineering predictive models, and extracting business insights."
    }
}

_model = None

def get_sentence_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[Screening Warning] Could not load SentenceTransformer: {e}")
            _model = None
    return _model

def screen_resume(parsed_resume_data, target_role="Software Engineer"):
    """
    Computes an NLP-based resume relevance screening score:
    1. Keyword Match (Hard and Soft Skills)
    2. Semantic Similarity between candidate profile and role description
    """
    role_info = ROLE_REQUIREMENTS.get(target_role, ROLE_REQUIREMENTS["Software Engineer"])
    candidate_tech = [s.title() for s in parsed_resume_data.get("technical_skills", [])]
    candidate_soft = [s.title() for s in parsed_resume_data.get("soft_skills", [])]
    all_candidate_skills = set(candidate_tech + candidate_soft)
    
    req_skills = set(s.title() for s in role_info["required_skills"])
    pref_skills = set(s.title() for s in role_info["preferred_skills"])
    
    matched_req = req_skills.intersection(all_candidate_skills)
    matched_pref = pref_skills.intersection(all_candidate_skills)
    
    req_score = (len(matched_req) / max(1, len(req_skills))) * 60.0
    pref_score = (len(matched_pref) / max(1, len(pref_skills))) * 20.0
    
    # NLP Semantic Similarity
    semantic_score = 15.0 # default baseline
    model = get_sentence_model()
    if model and parsed_resume_data.get("raw_text"):
        try:
            # Compare role description with candidate summary
            emb_role = model.encode(role_info["description"])
            candidate_summary = f"{parsed_resume_data.get('education', '')} {' '.join(candidate_tech)} {parsed_resume_data.get('experience', '')}"
            emb_cand = model.encode(candidate_summary[:512])
            
            # Cosine similarity
            cosine_sim = np.dot(emb_role, emb_cand) / (np.linalg.norm(emb_role) * np.linalg.norm(emb_cand) + 1e-8)
            semantic_score = float(np.clip((cosine_sim + 0.2) * 20.0, 0, 20.0))
        except Exception as e:
            print(f"[Screening Error] Semantic similarity error: {e}")

    total_score = min(100.0, req_score + pref_score + semantic_score)

    return {
        "target_role": target_role,
        "screening_score": round(total_score, 1),
        "matched_required_skills": list(matched_req),
        "missing_required_skills": list(req_skills - matched_req),
        "matched_preferred_skills": list(matched_pref),
        "total_skills_count": len(all_candidate_skills)
    }
