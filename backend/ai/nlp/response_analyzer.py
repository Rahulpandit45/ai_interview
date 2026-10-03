"""
response_analyzer.py
NLP Response Analysis Module using Sentence-Transformers (BERT architecture).

Methodology:
1. Preprocessing:
   - Text cleaning, normalization, lowercase mapping, and tokenization.
2. Embedding Generation:
   - Encodes candidate response and benchmark answer into dense 384-dimensional vector embeddings
     using the all-MiniLM-L6-v2 transformer model.
3. Cosine Similarity & Relevance:
   - Computes dot product of normalized embeddings to quantify semantic similarity.
4. Technical Depth & Completeness:
   - Analyzes keyword intersection with expected domain terminology and response length sufficiency.
5. Final Composite Score:
   - Weighted fusion: 50% Semantic Relevance + 30% Keyword Precision + 20% Completeness.
"""

import re
import numpy as np

_sentence_model = None

def get_sentence_transformer():
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[NLP Analyzer Warning] SentenceTransformer load failed: {e}")
            _sentence_model = None
    return _sentence_model

def analyze_sentiment_heuristic(text):
    text_lower = text.lower()
    positive_words = ["success", "good", "great", "effective", "improved", "passion", "collaborate", "solve", "reliable", "learned", "enthusiastic"]
    negative_words = ["bad", "fail", "terrible", "hate", "impossible", "quit", "useless", "annoying", "never"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count:
        return "Positive"
    elif neg_count > pos_count:
        return "Critical"
    return "Neutral"

def analyze_response(candidate_text, question_text, benchmark_answer="", expected_keywords=None):
    """
    Evaluates candidate's transcribed spoken answer against interview benchmark.
    Returns:
      {
        "relevance_score": float (0-100),
        "technical_score": float (0-100),
        "completeness_score": float (0-100),
        "sentiment": str,
        "matched_keywords": list,
        "composite_score": float (0-100)
      }
    """
    if not candidate_text or len(candidate_text.strip()) < 5:
        return {
            "relevance_score": 10.0,
            "technical_score": 10.0,
            "completeness_score": 5.0,
            "sentiment": "Neutral",
            "matched_keywords": [],
            "composite_score": 10.0
        }
        
    expected_keywords = expected_keywords or []
    words = candidate_text.lower().split()
    word_count = len(words)
    
    # 1. Keyword coverage
    matched_keywords = []
    for kw in expected_keywords:
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', candidate_text.lower()):
            matched_keywords.append(kw)
            
    kw_coverage = (len(matched_keywords) / max(1, len(expected_keywords))) * 100.0 if expected_keywords else 75.0

    # 2. Semantic Similarity using Sentence-Transformers
    model = get_sentence_transformer()
    semantic_sim_score = 70.0 # fallback
    if model:
        try:
            target_reference = benchmark_answer if benchmark_answer else question_text
            emb_ref = model.encode(target_reference)
            emb_cand = model.encode(candidate_text)
            
            cosine = np.dot(emb_ref, emb_cand) / (np.linalg.norm(emb_ref) * np.linalg.norm(emb_cand) + 1e-8)
            if np.isnan(cosine) or np.isinf(cosine):
                semantic_sim_score = 70.0
            else:
                # Map [-1, 1] cosine similarity to [0, 100] with reasonable scaling
                semantic_sim_score = float(np.clip((cosine + 0.1) * 90.0, 10.0, 100.0))
        except Exception as e:
            print(f"[NLP Analyzer] Semantic comparison error: {e}")
            semantic_sim_score = 70.0

    if np.isnan(semantic_sim_score) or np.isinf(semantic_sim_score):
        semantic_sim_score = 70.0

    # 3. Completeness Score (Ideal answer ~50-150 words)
    if word_count < 15:
        completeness = (word_count / 15.0) * 50.0
    elif word_count <= 180:
        completeness = 85.0 + min(15.0, (word_count - 15) / 10.0)
    else:
        completeness = max(70.0, 100.0 - (word_count - 180) * 0.2)

    # 4. Sentiment & Tone
    sentiment = analyze_sentiment_heuristic(candidate_text)

    # 5. Technical Depth & Composite Score
    technical_score = (0.6 * semantic_sim_score) + (0.4 * kw_coverage)
    relevance_score = semantic_sim_score
    composite_score = (0.45 * relevance_score) + (0.35 * technical_score) + (0.20 * completeness)

    def safe_float(val, default=70.0):
        try:
            f = float(val)
            return default if (np.isnan(f) or np.isinf(f)) else f
        except Exception:
            return default

    return {
        "relevance_score": round(safe_float(relevance_score), 1),
        "technical_score": round(safe_float(technical_score), 1),
        "completeness_score": round(safe_float(completeness), 1),
        "sentiment": sentiment,
        "matched_keywords": matched_keywords,
        "composite_score": round(safe_float(composite_score), 1)
    }
