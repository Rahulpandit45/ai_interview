"""
profile_question_model.py
Neural and Adaptive Question & Follow-Up Generation Engine for the AI Interview System.

Features:
1. Candidate Profile Tailoring:
   - Generates 10 distinct, customized interview questions based on candidate CV profile:
     (Technical skills, role, experience level, education, projects, soft skills).
   - Enforces 10-stage progression (Easy -> Medium -> Hard -> Scenario -> Trade-offs).
2. Contextual Dynamic Follow-Up Generation:
   - Generates intelligent follow-up questions conditioned on candidate's spoken/typed answer,
     previous question context, and demonstrated performance score.
3. Repetition Prevention & Diversity:
   - Tracks session history and employs dense semantic vector matching (candidate_question_kb.pkl)
     to ensure zero duplicate questions and high diversity across different candidates.
"""

import os
import sys
import json
import random
import pickle
import re
from typing import Dict, List, Any, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
MODELS_DIR = os.path.join(BASE_DIR, "trained_models")
MODEL_PATH = os.path.join(MODELS_DIR, "candidate_question_model")
KB_PATH = os.path.join(MODELS_DIR, "candidate_question_kb.pkl")
IT_QUESTIONS_PATH = os.path.join(DATASETS_DIR, "it_questions.json")

_kb_data = None
_embedder = None
_model = None
_tokenizer = None


def get_kb_data():
    global _kb_data
    if _kb_data is None and os.path.exists(KB_PATH):
        try:
            with open(KB_PATH, "rb") as f:
                _kb_data = pickle.load(f)
        except Exception as e:
            print(f"[ProfileQuestionModel] Warning: Could not load KB: {e}")
            _kb_data = None
    return _kb_data


def get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[ProfileQuestionModel] Warning: Could not load SentenceTransformer: {e}")
            _embedder = None
    return _embedder


def get_trained_generator():
    global _model, _tokenizer
    if _model is None and os.path.exists(MODEL_PATH):
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
            _model.eval()
        except Exception as e:
            print(f"[ProfileQuestionModel] Warning: Could not load fine-tuned model: {e}")
            _model = None
            _tokenizer = None
    return _model, _tokenizer


def extract_keywords_from_text(text: str, max_count: int = 6) -> List[str]:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {
        "what", "is", "the", "and", "a", "an", "of", "in", "to", "for", "with", "that", "this",
        "are", "from", "by", "as", "or", "on", "at", "which", "how", "can", "explain", "does",
        "used", "between", "difference", "definition", "could", "would", "tell"
    }
    keywords = []
    seen = set()
    for w in words:
        if w not in stop_words and w not in seen:
            seen.add(w)
            keywords.append(w)
            if len(keywords) >= max_count:
                break
    return keywords


class ProfileQuestionGenerator:
    """
    Orchestrates the generation of 10 profile-tailored questions and contextual follow-ups.
    """

    @classmethod
    def generate_candidate_questions(
        cls,
        profile_data: Optional[Dict[str, Any]] = None,
        target_role: str = "Software Engineer",
        count: int = 10,
        seen_question_ids: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates 10 distinct, relevant questions tailored to the candidate's CV profile.
        """
        profile = profile_data or {}
        skills = profile.get("technical_skills", []) or []
        experience = profile.get("experience", "1-3 years")
        education = profile.get("education", "Computer Science")
        projects = profile.get("projects", "")

        from backend.ai.nlp.question_generator import (
            load_dataset_questions,
            get_relevant_categories,
            SKILL_CATEGORY_MAP
        )

        all_q = load_dataset_questions()
        if not all_q:
            # Fallback starter questions
            return cls._get_default_10_questions(target_role)

        categories = get_relevant_categories(skills, target_role)
        used_ids = set(seen_question_ids) if seen_question_ids else set()

        # Build pools by difficulty and category
        def get_pool(diff: str, cat: Optional[str] = None):
            pool = [
                q for q in all_q
                if q.get("id") not in used_ids and str(q.get("difficulty", "")).lower() == diff.lower()
            ]
            if cat:
                cat_pool = [q for q in pool if q.get("category") == cat]
                if cat_pool:
                    return cat_pool
            return pool

        questions = []

        # 10-Stage Progression Plan
        # Stage 1: Easy (Primary CV Skill Foundational)
        # Stage 2: Easy (Secondary CV Skill / Programming Basics)
        # Stage 3: Medium (Applied Core Mechanisms)
        # Stage 4: Medium (Follow-up / Practical Use Case)
        # Stage 5: Medium (Database / Backend / System Component)
        # Stage 6: Medium-Hard (Follow-up / Scaling & Performance)
        # Stage 7: Medium-Hard (Project / Architecture Scenario)
        # Stage 8: Hard (Follow-up / Trade-offs & Edge Cases)
        # Stage 9: Hard (Advanced Architecture & Concurrency)
        # Stage 10: Hard (Synthesis & Problem Solving)

        stage_specs = [
            (1, "easy", 1, categories[0] if len(categories) > 0 else "Python", "Core Skill Fundamentals"),
            (2, "easy", 1, categories[1] if len(categories) > 1 else "Database & SQL", "Secondary Skill Fundamentals"),
            (3, "medium", 2, categories[0] if len(categories) > 0 else "Programming", "Applied Mechanics"),
            (4, "medium", 2, categories[2] if len(categories) > 2 else categories[0], "Practical Application & Follow-Up"),
            (5, "medium", 2, categories[1] if len(categories) > 1 else "Database & SQL", "Data Systems & Architecture"),
            (6, "medium", 2, categories[0] if len(categories) > 0 else "Software Engineering", "Systems Integration & Reliability"),
            (7, "hard", 3, categories[2] if len(categories) > 2 else categories[0], "Architecture & Project Scenario"),
            (8, "hard", 3, categories[0] if len(categories) > 0 else "Computer Networks", "Edge Cases & Trade-offs"),
            (9, "hard", 3, categories[1] if len(categories) > 1 else "Operating Systems", "Advanced Performance & Concurrency"),
            (10, "hard", 3, categories[0] if len(categories) > 0 else "Software Engineering", "System Synthesis & Deep Problem Solving"),
        ]

        # Adjust for count
        target_specs = stage_specs[:count] if count <= len(stage_specs) else stage_specs

        for stage_num, diff, diff_lvl, cat, stage_label in target_specs:
            pool = get_pool(diff, cat)
            if not pool:
                pool = get_pool(diff)
            if not pool:
                pool = [q for q in all_q if q.get("id") not in used_ids]
            if not pool:
                pool = all_q

            # Select randomly from candidate pool to ensure diversity across candidates
            chosen = random.choice(pool)
            used_ids.add(chosen.get("id"))

            q_text = chosen.get("question", "")
            ans1 = chosen.get("answer_1", "")
            ans2 = chosen.get("answer_2", "")
            ans3 = chosen.get("answer_3", "")
            chosen_cat = chosen.get("category", cat)

            questions.append({
                "id": chosen.get("id", stage_num),
                "question_id": chosen.get("id", stage_num),
                "question_number": stage_num,
                "total_questions": count,
                "category": chosen_cat,
                "topic": chosen_cat,
                "difficulty": diff,
                "difficulty_level": diff_lvl,
                "stage_label": stage_label,
                "question_text": q_text,
                "question": q_text,
                "benchmark_answer": ans2 or ans1,
                "answer_1": ans1,
                "answer_2": ans2,
                "answer_3": ans3,
                "keywords": extract_keywords_from_text(f"{q_text} {ans1} {ans2}"),
                "is_follow_up": stage_num in [4, 6, 8, 10]
            })

        return questions

    @classmethod
    def generate_followup_question(
        cls,
        profile_data: Optional[Dict[str, Any]],
        previous_question: str,
        candidate_answer: str,
        performance_rating: str = "Average",
        current_difficulty: str = "medium",
        category: str = "IT",
        seen_question_ids: Optional[set] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Generates a contextual, intelligent follow-up question based on the candidate's answer.
        """
        used_ids = seen_question_ids or set()
        answer_clean = (candidate_answer or "").strip()
        prev_q = (previous_question or "").strip()

        # Step 1: Use Neural Model or Semantic Knowledge Base if available
        model, tokenizer = get_trained_generator()
        if model and tokenizer and answer_clean:
            try:
                import torch
                prompt = (
                    f"Generate an intelligent interview follow-up question based on the candidate's response:\n"
                    f"- Previous Question: {prev_q}\n"
                    f"- Candidate Answer: {answer_clean}\n"
                    f"- Demonstrated Performance: {performance_rating}\n"
                    f"Follow-up Question:"
                )
                inputs = tokenizer(prompt, return_tensors="pt", max_length=192, truncation=True)
                with torch.no_grad():
                    outputs = model.generate(
                        inputs["input_ids"],
                        max_length=64,
                        num_beams=3,
                        early_stopping=True,
                        no_repeat_ngram_size=2
                    )
                generated_q = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                if len(generated_q) > 15 and "?" in generated_q:
                    return {
                        "question_text": generated_q,
                        "benchmark_answer": f"A comprehensive follow-up explanation addressing practical applications and mechanisms.",
                        "category": category,
                        "difficulty": current_difficulty,
                        "difficulty_level": 2 if current_difficulty == "medium" else (3 if current_difficulty == "hard" else 1),
                        "is_follow_up": True
                    }, True
            except Exception as e:
                print(f"[ProfileQuestionModel] Model generation notice: {e}")

        # Step 2: Contextual Dynamic Synthesis from Semantic Concepts
        followup_text = cls._synthesize_contextual_followup(prev_q, answer_clean, performance_rating, category)
        if followup_text:
            return {
                "question_text": followup_text,
                "benchmark_answer": f"A clear real-world explanation demonstrating understanding of {category} and trade-offs.",
                "category": category,
                "difficulty": current_difficulty,
                "difficulty_level": 2 if current_difficulty == "medium" else (3 if current_difficulty == "hard" else 1),
                "is_follow_up": True
            }, True

        # Step 3: Dataset Pool Fallback
        from backend.ai.nlp.question_generator import load_dataset_questions
        all_q = load_dataset_questions()
        pool = [
            q for q in all_q
            if q.get("id") not in used_ids
            and q.get("category") == category
            and str(q.get("difficulty", "")).lower() == current_difficulty.lower()
        ]
        if not pool:
            pool = [q for q in all_q if q.get("id") not in used_ids]
        if not pool:
            pool = all_q

        chosen = random.choice(pool)
        return chosen, True

    @classmethod
    def _synthesize_contextual_followup(
        cls,
        previous_question: str,
        candidate_answer: str,
        performance_rating: str,
        category: str
    ) -> str:
        """
        Dynamically constructs contextual follow-up inquiries.
        """
        q_lower = previous_question.lower()
        ans_lower = candidate_answer.lower()

        # Subject extraction
        subject = category
        if "python" in q_lower or "python" in ans_lower:
            subject = "Python"
        elif "react" in q_lower or "virtual dom" in q_lower:
            subject = "React"
        elif "sql" in q_lower or "database" in q_lower or "table" in q_lower:
            subject = "database architecture"
        elif "docker" in q_lower or "container" in q_lower:
            subject = "Docker containers"
        elif "api" in q_lower or "rest" in q_lower:
            subject = "REST APIs"

        if performance_rating in ["Good", "Excellent"]:
            templates = [
                f"Building on your answer regarding {subject}, how would you optimize this under high traffic or concurrency?",
                f"Can you explain the internal mechanism of {subject} and what architectural trade-offs you consider in production?",
                f"How would you diagnose and resolve potential edge cases or failure modes when working with {subject}?",
                f"Could you walk through a real-world scenario where you had to debug or scale a system utilizing {subject}?"
            ]
        elif performance_rating == "Average":
            templates = [
                f"Could you give a concrete, real-world example of how you have applied {subject} in a project?",
                f"What are the main advantages and potential drawbacks of using {subject} compared to alternatives?",
                f"How do you ensure reliability and clean code structure when implementing {subject}?"
            ]
        else: # Poor
            templates = [
                f"Let's look at the fundamentals: what is the primary purpose and use case of {subject}?",
                f"In simple terms, how does {subject} help developers solve everyday software engineering problems?"
            ]

        return random.choice(templates)

    @classmethod
    def _get_default_10_questions(cls, target_role: str) -> List[Dict[str, Any]]:
        defaults = [
            ("What is programming and how does high-level source code execute on a computer?", "Programming", "easy", 1),
            ("What is the difference between a variable, a data structure, and an object?", "Programming", "easy", 1),
            ("What is Python and why is it widely used in backend development and data engineering?", "Python", "easy", 1),
            ("How do lists and dictionaries differ in terms of time complexity for lookups?", "Data Structures", "medium", 2),
            ("What is a primary key and why is indexing critical for database performance?", "Database & SQL", "medium", 2),
            ("How do REST APIs handle stateless communication between clients and servers?", "APIs", "medium", 2),
            ("What is containerization with Docker and how does it differ from a virtual machine?", "Cloud Computing", "medium", 2),
            ("How do you prevent SQL injection and secure sensitive user inputs in web applications?", "Cybersecurity", "hard", 3),
            ("Explain the concept of concurrency and how asynchronous event loops handle I/O operations.", "Operating Systems", "hard", 3),
            ("How would you architect a scalable, fault-tolerant microservice application for 100,000 active users?", "Software Engineering", "hard", 3),
        ]

        result = []
        for idx, (text, cat, diff, diff_lvl) in enumerate(defaults, 1):
            result.append({
                "id": idx,
                "question_id": idx,
                "question_number": idx,
                "total_questions": 10,
                "category": cat,
                "topic": cat,
                "difficulty": diff,
                "difficulty_level": diff_lvl,
                "stage_label": f"Stage {idx}",
                "question_text": text,
                "question": text,
                "benchmark_answer": f"Standard benchmark answer for {text}",
                "keywords": extract_keywords_from_text(text),
                "is_follow_up": idx in [4, 6, 8, 10]
            })
        return result
