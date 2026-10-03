"""
question_generator.py
Dynamic skill-based and difficulty-tiered interview question generator.

Exclusively selects questions from the trained IT dataset (train_model.py / it_questions.json):
- Questions are concise, clear, and direct IT questions (no long paragraphs or essay scenarios).
- Exactly 3 benchmark answers available for every question (Answer 1: short, Answer 2: standard, Answer 3: detailed).
- Enforces strict progression:
    * Stage 1: EASY (Foundational IT / Core Skill Concept)
    * Stage 2: EASY (Technical Skill Concept)
    * Stage 3: MEDIUM (Intermediate Application & Core Mechanisms)
    * Stage 4: MEDIUM (Practical Systems / Trade-offs Concept)
    * Stage 5: HARD (Advanced Deep-Dive / Architecture / Memory / Concurrency)
"""

import os
import json
import random
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "it_questions.json")

# Category mapping from candidate skills to dataset categories
SKILL_CATEGORY_MAP = {
    "python": "Python",
    "py": "Python",
    "django": "Python",
    "flask": "Python",
    "fastapi": "Python",
    
    "sql": "Database & SQL",
    "mysql": "Database & SQL",
    "postgresql": "Database & SQL",
    "postgres": "Database & SQL",
    "sqlite": "Database & SQL",
    "database": "Database & SQL",
    "rdbms": "Database & SQL",
    "nosql": "Database & SQL",
    
    "javascript": "HTML/CSS/JavaScript",
    "js": "HTML/CSS/JavaScript",
    "html": "HTML/CSS/JavaScript",
    "css": "HTML/CSS/JavaScript",
    "react": "Web Development",
    "react.js": "Web Development",
    "vue": "Web Development",
    "node": "Web Development",
    "node.js": "Web Development",
    "web": "Web Development",
    "frontend": "Web Development",
    "backend": "Web Development",
    
    "java": "Java",
    "spring": "Java",
    
    "c": "C/C++",
    "c++": "C/C++",
    "cpp": "C/C++",
    "c/c++": "C/C++",
    
    "oop": "OOP",
    "object-oriented": "OOP",
    "object oriented": "OOP",
    
    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "algorithms": "Data Structures",
    
    "os": "Operating Systems",
    "operating system": "Operating Systems",
    "linux": "Operating Systems",
    "unix": "Operating Systems",
    
    "networking": "Computer Networks",
    "network": "Computer Networks",
    "tcp": "Computer Networks",
    "ip": "Computer Networks",
    "http": "Computer Networks",
    
    "api": "APIs",
    "apis": "APIs",
    "rest": "APIs",
    "restful": "APIs",
    "graphql": "APIs",
    
    "git": "Git/GitHub",
    "github": "Git/GitHub",
    "version control": "Git/GitHub",
    
    "ai": "AI & Machine Learning",
    "ml": "AI & Machine Learning",
    "machine learning": "AI & Machine Learning",
    "deep learning": "AI & Machine Learning",
    "nlp": "AI & Machine Learning",
    "pytorch": "AI & Machine Learning",
    "tensorflow": "AI & Machine Learning",
    
    "cloud": "Cloud Computing",
    "aws": "Cloud Computing",
    "azure": "Cloud Computing",
    "gcp": "Cloud Computing",
    "docker": "Cloud Computing",
    "kubernetes": "Cloud Computing",
    
    "cybersecurity": "Cybersecurity",
    "security": "Cybersecurity",
    
    "flutter": "Flutter",
    "dart": "Flutter",
    "mobile": "Flutter",
    
    "firebase": "Firebase",
    "iot": "IoT",
    
    "software engineering": "Software Engineering",
    "agile": "Software Engineering",
    "scrum": "Software Engineering"
}

_dataset_cache = None

def load_dataset_questions():
    """Loads beginner-to-intermediate IT questions from it_questions.json."""
    global _dataset_cache
    if _dataset_cache is not None:
        return _dataset_cache

    if os.path.exists(DATASET_PATH):
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                _dataset_cache = json.load(f)
                return _dataset_cache
        except Exception as e:
            print(f"[Question Generator] Error loading {DATASET_PATH}: {e}")

    # Fallback to local root it_questions.json if exists
    fallback_path = os.path.join(os.path.dirname(BASE_DIR), "it_questions.json")
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                _dataset_cache = json.load(f)
                return _dataset_cache
        except Exception as e:
            print(f"[Question Generator] Error loading fallback {fallback_path}: {e}")

    _dataset_cache = []
    return _dataset_cache


def extract_keywords(question_text, answer_1="", answer_2="", category=""):
    """Extracts salient keywords from the question and answers."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', f"{question_text} {answer_1} {answer_2}".lower())
    stop_words = {
        "what", "is", "the", "and", "a", "an", "of", "in", "to", "for", "with", "that", "this",
        "are", "from", "by", "as", "or", "on", "at", "which", "how", "can", "explain", "does",
        "used", "between", "difference", "explain", "definition"
    }
    filtered = [w for w in words if w not in stop_words]
    # Preserve order of appearance, limit to 6
    seen = set()
    keywords = []
    if category:
        cat_lower = category.lower()
        if " " not in cat_lower:
            keywords.append(cat_lower)
            seen.add(cat_lower)
    for w in filtered:
        if w not in seen:
            seen.add(w)
            keywords.append(w)
        if len(keywords) >= 6:
            break
    return keywords


def get_relevant_categories(candidate_skills, target_role="Software Engineer"):
    """Determines prioritized dataset categories based on candidate skills and role."""
    matched_cats = []
    skills_lower = [s.lower().strip() for s in (candidate_skills or [])]

    for skill in skills_lower:
        for k, cat in SKILL_CATEGORY_MAP.items():
            if k in skill or skill in k:
                if cat not in matched_cats:
                    matched_cats.append(cat)

    role_lower = (target_role or "").lower()
    if "python" in role_lower and "Python" not in matched_cats:
        matched_cats.insert(0, "Python")
    if ("web" in role_lower or "frontend" in role_lower) and "Web Development" not in matched_cats:
        matched_cats.append("Web Development")
    if ("backend" in role_lower or "database" in role_lower) and "Database & SQL" not in matched_cats:
        matched_cats.append("Database & SQL")
    if ("ai" in role_lower or "data" in role_lower or "machine learning" in role_lower) and "AI & Machine Learning" not in matched_cats:
        matched_cats.append("AI & Machine Learning")

    # Foundational defaults if not enough categories matched
    default_order = [
        "Programming",
        "Computer Fundamentals",
        "Python",
        "Database & SQL",
        "Data Structures",
        "OOP",
        "Software Engineering",
        "Web Development",
        "Computer Networks",
        "Operating Systems",
        "Git/GitHub",
        "APIs"
    ]
    for cat in default_order:
        if cat not in matched_cats:
            matched_cats.append(cat)

    return matched_cats


def generate_interview_questions(parsed_resume_data=None, target_role="Software Engineer", count=5):
    """
    Generates interview questions strictly from the trained dataset (it_questions.json),
    ordered progressively from EASY to HARD:
      - Question 1 [EASY]: Foundational concept (difficulty_level = 1)
      - Question 2 [EASY]: Primary technical skill concept (difficulty_level = 1)
      - Question 3 [MEDIUM]: Intermediate application / concept (difficulty_level = 2)
      - Question 4 [MEDIUM]: Technical systems / trade-offs concept (difficulty_level = 2)
      - Question 5 [HARD]: Advanced deep-dive / architecture concept (difficulty_level = 3)
    """
    all_dataset = load_dataset_questions()
    if not all_dataset:
        # Extreme fallback if dataset is missing
        return [
            {
                "id": 1,
                "category": "Programming",
                "difficulty": "easy",
                "difficulty_level": 1,
                "question_text": "What is programming?",
                "benchmark_answer": "Programming is the process of writing instructions for computers using programming languages to solve problems or perform tasks.",
                "answer_1": "Programming is writing code for computers.",
                "answer_2": "Programming is the process of creating a set of instructions that tell a computer how to perform a task.",
                "answer_3": "Programming involves designing, writing, testing, and maintaining source code using programming languages like Python, C++, or Java.",
                "keywords": ["programming", "code", "computer", "instructions", "language"]
            }
        ]

    candidate_skills = parsed_resume_data.get("technical_skills", []) if parsed_resume_data else []
    target_categories = get_relevant_categories(candidate_skills, target_role)

    # Split dataset questions by difficulty
    easy_pool = [q for q in all_dataset if q.get("difficulty", "").lower() == "easy"]
    medium_pool = [q for q in all_dataset if q.get("difficulty", "").lower() == "medium"]
    hard_pool = [q for q in all_dataset if q.get("difficulty", "").lower() == "hard"]

    # Filter by candidate categories if possible
    def filter_by_cats(pool, cats):
        matched = [q for q in pool if q.get("category") in cats]
        return matched if matched else pool

    easy_matched = filter_by_cats(easy_pool, target_categories)
    medium_matched = filter_by_cats(medium_pool, target_categories)
    hard_matched = filter_by_cats(hard_pool, target_categories)

    selected_raw = []
    used_ids = set()

    def pick_question(pool, preferred_cat=None):
        nonlocal used_ids
        candidates = [q for q in pool if q.get("id") not in used_ids]
        if not candidates:
            candidates = pool
        if preferred_cat:
            cat_candidates = [q for q in candidates if q.get("category") == preferred_cat]
            if cat_candidates:
                chosen = random.choice(cat_candidates)
                used_ids.add(chosen.get("id"))
                return chosen
        chosen = random.choice(candidates)
        used_ids.add(chosen.get("id"))
        return chosen

    # Pick strictly according to count:
    # If count == 5:
    # Q1: Easy (Foundational / Primary Skill)
    # Q2: Easy (Secondary Skill / Programming)
    # Q3: Medium (Skill Application)
    # Q4: Medium (Skill Mechanism / Trade-off)
    # Q5: Hard (Advanced Concept)
    primary_cat = target_categories[0] if target_categories else "Python"
    secondary_cat = target_categories[1] if len(target_categories) > 1 else "Database & SQL"
    tertiary_cat = target_categories[2] if len(target_categories) > 2 else primary_cat

    # Question 1: EASY
    q1 = pick_question(easy_matched, preferred_cat=primary_cat)
    selected_raw.append((q1, "easy", 1))

    # Question 2: EASY
    q2 = pick_question(easy_matched, preferred_cat=secondary_cat)
    selected_raw.append((q2, "easy", 1))

    # Question 3: MEDIUM
    q3 = pick_question(medium_matched, preferred_cat=primary_cat)
    selected_raw.append((q3, "medium", 2))

    # Question 4: MEDIUM
    q4 = pick_question(medium_matched, preferred_cat=tertiary_cat)
    selected_raw.append((q4, "medium", 2))

    # Question 5: HARD
    q5 = pick_question(hard_matched, preferred_cat=primary_cat)
    selected_raw.append((q5, "hard", 3))

    # If count is different from 5, adjust
    if count < len(selected_raw):
        selected_raw = selected_raw[:count]
    elif count > len(selected_raw):
        while len(selected_raw) < count:
            extra_q = pick_question(medium_matched)
            selected_raw.append((extra_q, "medium", 2))

    # Sort strictly by difficulty level (Easy -> Medium -> Hard)
    difficulty_order = {"easy": 1, "medium": 2, "hard": 3}
    selected_raw.sort(key=lambda x: difficulty_order.get(x[1], 1))

    # Build standardized question dictionaries
    final_questions = []
    for idx, (item, diff_str, diff_lvl) in enumerate(selected_raw, 1):
        q_text = item["question"]
        ans1 = item.get("answer_1", "")
        ans2 = item.get("answer_2", "")
        ans3 = item.get("answer_3", "")
        cat = item.get("category", "IT")

        final_questions.append({
            "id": idx,
            "category": cat,
            "difficulty": diff_str,
            "difficulty_level": diff_lvl,
            "question_text": q_text,
            "benchmark_answer": ans2 or ans1,
            "answer_1": ans1,
            "answer_2": ans2,
            "answer_3": ans3,
            "keywords": extract_keywords(q_text, ans1, ans2, cat)
        })

    return final_questions
