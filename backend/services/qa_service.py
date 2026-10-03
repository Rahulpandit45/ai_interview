"""
qa_service.py
IT Question & Answer inference service for the AI Interview System.

Architecture:
1. Semantic Similarity Matching:
   - Uses sentence-transformers (all-MiniLM-L6-v2) and precomputed knowledge base embeddings
     (backend/trained_models/it_qa_kb.pkl) to find the closest matching IT concept.
   - Robust to different phrasings and synonyms (e.g., "What is Python?", "Tell me about Python",
     "Can you explain the Python language?", "Define Python").
2. Generative Seq2Seq Language Model:
   - Uses fine-tuned google/flan-t5-small (backend/trained_models/it_qa_model) for direct
     sequence generation.
3. Unified Output:
   - Returns standard schema: {"question": "...", "answer": "..."}
"""

import os
import sys
import pickle
import numpy as np
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "trained_models")
KB_PATH = os.path.join(MODELS_DIR, "it_qa_kb.pkl")
SEQ2SEQ_MODEL_DIR = os.path.join(MODELS_DIR, "it_qa_model")

_embedder = None
_kb_data = None
_seq2seq_model = None
_seq2seq_tokenizer = None


def get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[QA Service] Warning: Failed to load SentenceTransformer: {e}")
            _embedder = None
    return _embedder


def get_kb_data():
    global _kb_data
    if _kb_data is None:
        if os.path.exists(KB_PATH):
            try:
                with open(KB_PATH, "rb") as f:
                    _kb_data = pickle.load(f)
            except Exception as e:
                print(f"[QA Service] Warning: Failed to load KB: {e}")
                _kb_data = None
    return _kb_data


def get_seq2seq_pipeline():
    global _seq2seq_model, _seq2seq_tokenizer
    if _seq2seq_model is None and os.path.exists(SEQ2SEQ_MODEL_DIR):
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            _seq2seq_tokenizer = AutoTokenizer.from_pretrained(SEQ2SEQ_MODEL_DIR)
            _seq2seq_model = AutoModelForSeq2SeqLM.from_pretrained(SEQ2SEQ_MODEL_DIR)
            _seq2seq_model.eval()
        except Exception as e:
            print(f"[QA Service] Warning: Failed to load Seq2Seq model: {e}")
            _seq2seq_model = None
            _seq2seq_tokenizer = None
    return _seq2seq_model, _seq2seq_tokenizer


class QAService:
    @staticmethod
    def answer_question(question: str, answer_style: str = "standard") -> dict:
        """
        Answers an IT interview question with semantic paraphrase tolerance.
        Returns:
            {
                "question": question,
                "answer": answer_text
            }
        """
        clean_q = (question or "").strip()
        if not clean_q:
            return {
                "question": question,
                "answer": "Please provide a valid IT question."
            }

        embedder = get_embedder()
        kb = get_kb_data()

        best_meta = None
        highest_sim = 0.0

        if embedder is not None and kb is not None and len(kb.get("embeddings", [])) > 0:
            try:
                q_emb = embedder.encode([clean_q], normalize_embeddings=True)[0]
                kb_embeddings = kb["embeddings"]  # Shape: (N, 384)
                similarities = np.dot(kb_embeddings, q_emb)
                best_idx = int(np.argmax(similarities))
                highest_sim = float(similarities[best_idx])

                if highest_sim >= 0.60:
                    best_meta = kb["metadata"][best_idx]
            except Exception as e:
                print(f"[QA Service] Semantic matching error: {e}")

        # If semantic match found in knowledge base
        if best_meta is not None:
            if answer_style == "short":
                chosen_answer = best_meta.get("answer_1") or best_meta.get("answer_2")
            elif answer_style == "detailed":
                chosen_answer = best_meta.get("answer_3") or best_meta.get("answer_2")
            else:
                # Standard simple explanation (Answer 2)
                chosen_answer = best_meta.get("answer_2") or best_meta.get("answer_1")

            return {
                "question": clean_q,
                "answer": chosen_answer
            }

        # Fallback to Seq2Seq generator if available
        model, tokenizer = get_seq2seq_pipeline()
        if model is not None and tokenizer is not None:
            try:
                prompt = f"Explain this IT interview question: {clean_q}"
                inputs = tokenizer(prompt, return_tensors="pt", max_length=128, truncation=True)
                with torch.no_grad():
                    outputs = model.generate(
                        inputs["input_ids"],
                        max_length=128,
                        num_beams=3,
                        early_stopping=True
                    )
                generated_answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                if generated_answer:
                    return {
                        "question": clean_q,
                        "answer": generated_answer
                    }
            except Exception as e:
                print(f"[QA Service] Generative fallback error: {e}")

        # Fallback default answer
        return {
            "question": clean_q,
            "answer": "This is a fundamental computer science concept. Further context is needed to provide a detailed explanation."
        }
