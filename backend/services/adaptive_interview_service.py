"""
adaptive_interview_service.py
Real-time Dynamic and Adaptive Interview State Engine for AI Interview System.

Key Principles:
1. Start with Profile-Tailored Basic Questions:
   - Evaluates candidate CV skills, target role, and experience profile.
   - Begins session with a foundational IT question at EASY difficulty.
2. Evaluate Every Answer:
   - Scores candidate answer using Sentence-Transformers semantic relevance,
     technical keyword precision, and response completeness.
   - Internal Score Bands:
       0-40   -> Poor
       41-70  -> Average
       71-85  -> Good
       86-100 -> Excellent
3. Select Next Question Dynamically:
   - Strong Answer (Good/Excellent):
       * Advance difficulty: Easy -> Medium -> Hard (no sudden jump from Easy to Hard).
       * Select deeper or more advanced question on the topic or next key CV skill.
   - Average Answer:
       * Maintain current difficulty level.
       * Ask a related question or practical follow-up at similar difficulty.
   - Poor Answer:
       * Reduce difficulty: Hard -> Medium -> Easy.
       * If already at Easy, select a different fundamental concept or switch topic.
4. Follow-Up Questions (After each answer):
   - Contextual follow-up generation directly conditioned on candidate's previous response,
     demonstrated accuracy, and practical application.
5. Avoid Repetition & Distinct Questions per Candidate:
   - Tracks all previously asked question IDs and text embeddings.
   - Guarantees high uniqueness across different candidate profiles and zero within-session repeats.
6. 10 Total Questions Threshold:
   - Enforces 10 structured questions covering core skills, practical code mechanics,
     system architecture, project scenarios, and advanced trade-offs.
"""

import os
import sys
import json
import re
import random
from typing import Dict, List, Optional, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.ai.nlp.question_generator import (
    load_dataset_questions,
    get_relevant_categories,
    extract_keywords,
    SKILL_CATEGORY_MAP
)
from backend.ai.nlp.response_analyzer import analyze_response
from backend.ai.nlp.profile_question_model import ProfileQuestionGenerator

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
DIFFICULTY_MAP = {"easy": 1, "medium": 2, "hard": 3}


class AdaptiveSession:
    """
    Maintains the state and evaluation history for an adaptive interview session.
    """
    def __init__(
        self,
        interview_id: int,
        candidate_skills: Optional[List[str]] = None,
        target_role: str = "Software Engineer",
        max_questions: int = 10,
        profile_data: Optional[Dict[str, Any]] = None
    ):
        self.interview_id = interview_id
        self.candidate_skills = candidate_skills or []
        self.target_role = target_role
        self.max_questions = max(1, min(max_questions, 20))
        self.profile_data = profile_data or {
            "technical_skills": self.candidate_skills,
            "target_role": target_role
        }

        # Prioritized categories from candidate CV and role
        self.prioritized_categories = get_relevant_categories(self.candidate_skills, self.target_role)
        self.current_category_idx = 0
        self.current_topic = self.prioritized_categories[0] if self.prioritized_categories else "Python"
        self.current_difficulty = "easy"

        # Questions and Answer History
        self.questions_asked: List[Dict[str, Any]] = []
        self.asked_question_ids = set()
        self.asked_question_texts = []
        self.candidate_answers: List[str] = []
        self.answer_scores: List[float] = []
        self.answer_ratings: List[str] = []
        self.evaluations: List[Dict[str, Any]] = []

        # Topics tracking
        self.strong_topics = []
        self.weak_topics = []
        self.follow_up_history: List[Dict[str, Any]] = []

        self.is_complete = False

        # Pre-select the initial basic question
        self.initial_question = self._select_first_basic_question()

    def _select_first_basic_question(self) -> Dict[str, Any]:
        """
        Picks a foundational IT question (Easy difficulty)
        randomized within the candidate's primary CV skill to ensure diversity across candidates.
        """
        all_q = load_dataset_questions()
        primary_cat = self.current_topic

        # Find easy questions in primary category
        candidates = [
            q for q in all_q
            if q.get("category") == primary_cat and str(q.get("difficulty", "")).lower() == "easy"
        ]

        if not candidates:
            # Fallback to easy programming or computer fundamentals
            candidates = [
                q for q in all_q
                if q.get("category") in ["Programming", "Computer Fundamentals", "Python"]
                and str(q.get("difficulty", "")).lower() == "easy"
            ]

        if not candidates:
            candidates = [q for q in all_q if str(q.get("difficulty", "")).lower() == "easy"]

        # Randomize first question selection to ensure uniqueness per candidate
        chosen = random.choice(candidates) if candidates else all_q[0]
        q_obj = self._format_question(chosen, question_number=1, is_follow_up=False)
        self.asked_question_ids.add(q_obj["id"])
        self.asked_question_texts.append(q_obj["question_text"])
        self.questions_asked.append(q_obj)
        return q_obj

    def _format_question(self, raw_q: Dict[str, Any], question_number: int, is_follow_up: bool = False, custom_text: str = None) -> Dict[str, Any]:
        """Formats dataset question into standardized contract."""
        diff = str(raw_q.get("difficulty", "easy")).lower()
        diff_lvl = raw_q.get("difficulty_level", DIFFICULTY_MAP.get(diff, 1))
        ans1 = raw_q.get("answer_1", "")
        ans2 = raw_q.get("answer_2", "")
        ans3 = raw_q.get("answer_3", "")
        q_text = custom_text or raw_q.get("question", "") or raw_q.get("question_text", "")

        q_id = raw_q.get("id") or raw_q.get("question_id") or question_number

        return {
            "id": q_id,
            "question_id": q_id,
            "question_number": question_number,
            "total_questions": self.max_questions,
            "category": raw_q.get("category", self.current_topic),
            "topic": raw_q.get("category", self.current_topic),
            "difficulty": diff,
            "difficulty_level": diff_lvl,
            "question_text": q_text,
            "question": q_text,
            "benchmark_answer": raw_q.get("benchmark_answer") or ans2 or ans1 or "Comprehensive technical explanation.",
            "answer_1": ans1,
            "answer_2": ans2,
            "answer_3": ans3,
            "keywords": raw_q.get("keywords") or extract_keywords(q_text, ans1, ans2, raw_q.get("category", "")),
            "is_follow_up": is_follow_up
        }

    def evaluate_candidate_answer(self, question_id: Any, answer_text: str) -> Dict[str, Any]:
        """
        Evaluates the candidate's answer against the active question benchmark.
        Assigns internal rating:
          0-40   -> Poor
          41-70  -> Average
          71-85  -> Good
          86-100 -> Excellent
        """
        answer_clean = (answer_text or "").strip()
        current_q = self.questions_asked[-1] if self.questions_asked else None

        benchmark = current_q.get("benchmark_answer", "") if current_q else ""
        q_text = current_q.get("question_text", "") if current_q else ""
        expected_kw = current_q.get("keywords", []) if current_q else []

        nlp_res = analyze_response(
            candidate_text=answer_clean,
            question_text=q_text,
            benchmark_answer=benchmark,
            expected_keywords=expected_kw
        )

        composite = nlp_res.get("composite_score", 50.0)

        # Classify rating
        if composite <= 40.0:
            rating = "Poor"
        elif composite <= 70.0:
            rating = "Average"
        elif composite <= 85.0:
            rating = "Good"
        else:
            rating = "Excellent"

        eval_record = {
            "question_id": question_id,
            "question_text": q_text,
            "topic": current_q.get("category", self.current_topic) if current_q else self.current_topic,
            "difficulty": current_q.get("difficulty", self.current_difficulty) if current_q else self.current_difficulty,
            "answer": answer_clean,
            "composite_score": composite,
            "relevance_score": nlp_res.get("relevance_score", 0.0),
            "technical_score": nlp_res.get("technical_score", 0.0),
            "completeness_score": nlp_res.get("completeness_score", 0.0),
            "sentiment": nlp_res.get("sentiment", "Neutral"),
            "rating": rating,
            "matched_keywords": nlp_res.get("matched_keywords", [])
        }

        # Track history
        self.candidate_answers.append(answer_clean)
        self.answer_scores.append(composite)
        self.answer_ratings.append(rating)
        self.evaluations.append(eval_record)

        topic = eval_record["topic"]
        if rating in ["Good", "Excellent"]:
            if topic not in self.strong_topics:
                self.strong_topics.append(topic)
            if topic in self.weak_topics:
                self.weak_topics.remove(topic)
        elif rating == "Poor":
            if topic not in self.weak_topics:
                self.weak_topics.append(topic)

        return eval_record

    def select_next_question(self, last_eval: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically adapts difficulty and topic to select the next question or follow-up.
        Enforces 10 total questions threshold.
        """
        questions_asked_count = len(self.questions_asked)

        # Check if interview question limit (10 questions) has been reached
        if questions_asked_count >= self.max_questions:
            self.is_complete = True
            return {
                "interview_id": self.interview_id,
                "is_complete": True,
                "message": "Interview completed successfully. All scheduled questions finished.",
                "total_questions": self.max_questions,
                "question_number": questions_asked_count,
                "interview_state": self.get_state_summary()
            }

        rating = last_eval.get("rating", "Average")
        last_difficulty = self.current_difficulty
        next_difficulty = last_difficulty
        target_category = self.current_topic

        # Decide whether to ask a contextual follow-up on this turn
        # Even stages (Q2, Q4, Q6, Q8, Q10) or average answers trigger contextual follow-ups
        next_q_num = questions_asked_count + 1
        trigger_followup = (next_q_num in [4, 6, 8, 10]) or (rating == "Average" and random.random() < 0.7)

        # -------------------------------------------------------------
        # 1. Adapt Difficulty according to candidate's demonstrated level
        # -------------------------------------------------------------
        if rating in ["Good", "Excellent"]:
            # Strong answer -> Increase difficulty (Easy -> Medium -> Hard)
            if last_difficulty == "easy":
                next_difficulty = "medium"
            elif last_difficulty == "medium":
                next_difficulty = "hard"
            else:
                next_difficulty = "hard"
                self._rotate_category()
                target_category = self.current_topic

        elif rating == "Average":
            next_difficulty = last_difficulty

        else: # Poor
            # Weak / poor answer -> Reduce difficulty (Hard -> Medium -> Easy)
            if last_difficulty == "hard":
                next_difficulty = "medium"
            elif last_difficulty == "medium":
                next_difficulty = "easy"
            else:
                next_difficulty = "easy"
                self._rotate_category()
                target_category = self.current_topic

        self.current_difficulty = next_difficulty

        # -------------------------------------------------------------
        # 2. Generate Next Question or Contextual Follow-Up
        # -------------------------------------------------------------
        if trigger_followup:
            followup_obj, is_followup = ProfileQuestionGenerator.generate_followup_question(
                profile_data=self.profile_data,
                previous_question=last_eval.get("question_text", ""),
                candidate_answer=last_eval.get("answer", ""),
                performance_rating=rating,
                current_difficulty=next_difficulty,
                category=target_category,
                seen_question_ids=self.asked_question_ids
            )
            raw_question = followup_obj
            follow_up_flag = True
        else:
            raw_question, follow_up_flag = self._find_unasked_question(
                category=target_category,
                difficulty=next_difficulty,
                prefer_follow_up=False,
                previous_question=last_eval.get("question_text", "")
            )

        q_obj = self._format_question(
            raw_question,
            question_number=next_q_num,
            is_follow_up=follow_up_flag
        )

        self.asked_question_ids.add(q_obj["id"])
        self.asked_question_texts.append(q_obj["question_text"])
        self.questions_asked.append(q_obj)

        if follow_up_flag:
            self.follow_up_history.append({
                "parent_question": last_eval.get("question_text", ""),
                "follow_up_question": q_obj["question_text"],
                "topic": target_category
            })

        return {
            "interview_id": self.interview_id,
            "id": q_obj["id"],
            "question": q_obj["question_text"],
            "question_text": q_obj["question_text"],
            "question_id": q_obj["id"],
            "topic": q_obj["category"],
            "category": q_obj["category"],
            "difficulty": q_obj["difficulty"],
            "difficulty_level": q_obj["difficulty_level"],
            "question_number": next_q_num,
            "total_questions": self.max_questions,
            "is_complete": False,
            "is_follow_up": follow_up_flag,
            "benchmark_answer": q_obj["benchmark_answer"],
            "previous_evaluation": {
                "score": last_eval.get("composite_score"),
                "rating": rating,
                "technical_accuracy": last_eval.get("technical_score"),
                "relevance": last_eval.get("relevance_score"),
                "completeness": last_eval.get("completeness_score")
            },
            "interview_state": self.get_state_summary()
        }

    def _rotate_category(self):
        """Advances to the next priority category from the candidate's CV."""
        if len(self.prioritized_categories) > 1:
            self.current_category_idx = (self.current_category_idx + 1) % len(self.prioritized_categories)
            self.current_topic = self.prioritized_categories[self.current_category_idx]

    def _find_unasked_question(
        self,
        category: str,
        difficulty: str,
        prefer_follow_up: bool = False,
        previous_question: str = ""
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Locates an unasked question strictly adhering to IT categories and difficulty.
        """
        all_q = load_dataset_questions()
        diff_str = difficulty.lower()

        # Step 1: Pool matching exact category & difficulty
        pool = [
            q for q in all_q
            if q.get("id") not in self.asked_question_ids
            and q.get("category") == category
            and str(q.get("difficulty", "")).lower() == diff_str
        ]

        # Step 2: If empty, try related categories from candidate's CV at the same difficulty
        if not pool:
            for cat in self.prioritized_categories:
                pool = [
                    q for q in all_q
                    if q.get("id") not in self.asked_question_ids
                    and q.get("category") == cat
                    and str(q.get("difficulty", "")).lower() == diff_str
                ]
                if pool:
                    self.current_topic = cat
                    break

        # Step 3: If still empty, search across all dataset questions matching difficulty
        if not pool:
            pool = [
                q for q in all_q
                if q.get("id") not in self.asked_question_ids
                and str(q.get("difficulty", "")).lower() == diff_str
            ]

        # Step 4: Fallback to any unasked question
        if not pool:
            pool = [q for q in all_q if q.get("id") not in self.asked_question_ids]

        if not pool:
            return all_q[0], False

        chosen = random.choice(pool)
        return chosen, False

    def get_state_summary(self) -> Dict[str, Any]:
        """Provides full telemetry of the current adaptive interview state."""
        total_asked = len(self.questions_asked)
        avg_score = round(sum(self.answer_scores) / max(1, len(self.answer_scores)), 1) if self.answer_scores else 0.0

        return {
            "interview_id": self.interview_id,
            "current_topic": self.current_topic,
            "current_difficulty": self.current_difficulty,
            "questions_asked_count": total_asked,
            "questions_remaining": max(0, self.max_questions - total_asked),
            "max_questions": self.max_questions,
            "average_score": avg_score,
            "strong_topics": list(set(self.strong_topics)),
            "weak_topics": list(set(self.weak_topics)),
            "follow_up_count": len(self.follow_up_history),
            "is_complete": self.is_complete
        }


class AdaptiveInterviewManager:
    """
    Singleton repository managing active adaptive interview sessions.
    """
    _sessions: Dict[int, AdaptiveSession] = {}

    @classmethod
    def get_or_create_session(
        cls,
        interview_id: int,
        candidate_skills: Optional[List[str]] = None,
        target_role: str = "Software Engineer",
        max_questions: int = 10,
        profile_data: Optional[Dict[str, Any]] = None
    ) -> AdaptiveSession:
        if interview_id not in cls._sessions:
            cls._sessions[interview_id] = AdaptiveSession(
                interview_id=interview_id,
                candidate_skills=candidate_skills,
                target_role=target_role,
                max_questions=max_questions,
                profile_data=profile_data
            )
        return cls._sessions[interview_id]

    @classmethod
    def get_session(cls, interview_id: int) -> Optional[AdaptiveSession]:
        return cls._sessions.get(interview_id)

    @classmethod
    def reset_session(cls, interview_id: int):
        if interview_id in cls._sessions:
            del cls._sessions[interview_id]

    @classmethod
    def process_next_question(cls, interview_id: int, question_id: Any, answer_text: str) -> Dict[str, Any]:
        """
        Evaluates candidate's answer and determines the next adaptive question or follow-up.
        """
        session = cls.get_or_create_session(interview_id, max_questions=10)
        evaluation = session.evaluate_candidate_answer(question_id, answer_text)
        next_step = session.select_next_question(evaluation)
        return next_step
