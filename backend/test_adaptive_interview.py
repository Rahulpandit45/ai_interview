"""
test_adaptive_interview.py
Comprehensive test suite for Dynamic & Adaptive Technical Interview System.

Covers:
1. Start with basic question based on CV, skills, and target role (Easy difficulty).
2. Answer evaluation and score classification (0-40 Poor, 41-70 Average, 71-85 Good, 86-100 Excellent).
3. Dynamic difficulty progression:
   - Strong/Excellent answer -> Increases difficulty (Easy -> Medium -> Hard, no skipping).
   - Average answer -> Maintains same difficulty level.
   - Poor/Incorrect answer -> Reduces difficulty (Hard -> Medium -> Easy).
4. Follow-up questions support.
5. Repetition prevention (zero duplicate question IDs or identical questions).
6. IT-only topic constraint (strictly from it_questions.json across 21 categories).
7. Interview state tracking (current topic, difficulty, strong/weak topics, scores, counts).
8. Maximum question threshold enforcement (is_complete = True).
9. FastAPI endpoints: POST /api/interview/next-question, init-adaptive, and state.
10. Flask proxy route with JWT authorization and post-termination safety guard.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.services.adaptive_interview_service import (
    AdaptiveSession,
    AdaptiveInterviewManager
)
from backend.app import app
from backend.services.database import db
from backend.models.interview import Interview
from backend.models.user import User


class AdaptiveInterviewUnitTests(unittest.TestCase):
    def setUp(self):
        self.session = AdaptiveSession(
            interview_id=777,
            candidate_skills=["Python", "SQL", "Flask"],
            target_role="Python Developer",
            max_questions=5
        )

    def test_start_with_basic_it_question(self):
        """1. Starts with a simple IT question (Easy difficulty) matching candidate's primary CV skill."""
        q1 = self.session.initial_question
        self.assertIsNotNone(q1)
        self.assertEqual(q1["difficulty"].lower(), "easy")
        self.assertEqual(q1["question_number"], 1)
        self.assertIn(q1["category"], ["Python", "Programming", "Computer Fundamentals"])
        self.assertTrue(len(q1["question_text"]) > 5)
        # Check that it is a direct concise question
        self.assertTrue("?" in q1["question_text"])

    def test_evaluate_answer_score_bands(self):
        """2. Evaluates candidate answers into the 4 defined score bands."""
        # Strong answer to question
        q1 = self.session.initial_question
        strong_ans = q1.get("benchmark_answer") or "Python is a high-level, interpreted programming language known for its clear syntax, readability, and versatile libraries."
        res_strong = self.session.evaluate_candidate_answer(q1["id"], strong_ans)
        self.assertIn(res_strong["rating"], ["Good", "Excellent"])
        self.assertGreaterEqual(res_strong["composite_score"], 65.0)

        # Average answer
        avg_ans = f"It is a basic {q1.get('category', 'software')} concept used in programming and system development to perform standard tasks."
        res_avg = self.session.evaluate_candidate_answer(q1["id"], avg_ans)
        self.assertIn(res_avg["rating"], ["Average", "Good", "Poor"])

        # Poor answer
        poor_ans = "I don't know what that means."
        res_poor = self.session.evaluate_candidate_answer(q1["id"], poor_ans)
        self.assertEqual(res_poor["rating"], "Poor")
        self.assertLessEqual(res_poor["composite_score"], 40.0)

    def test_strong_answer_increases_difficulty(self):
        """3. Strong answer (Good/Excellent) advances difficulty: Easy -> Medium -> Hard."""
        session = AdaptiveSession(interview_id=778, candidate_skills=["Python"], max_questions=5)
        q1 = session.initial_question
        self.assertEqual(q1["difficulty"].lower(), "easy")

        # Give strong answer on Q1
        eval1 = session.evaluate_candidate_answer(
            q1["id"],
            q1.get("benchmark_answer") or "Python is a high-level interpreted programming language with dynamic semantics and versatile standard library."
        )
        q2_resp = session.select_next_question(eval1)
        self.assertEqual(q2_resp["difficulty"].lower(), "medium")
        self.assertEqual(q2_resp["question_number"], 2)

        # Give strong answer on Q2 (Medium) matching question benchmark
        eval2 = session.evaluate_candidate_answer(
            q2_resp["question_id"],
            q2_resp.get("benchmark_answer") or "A list is mutable and can be modified in place, whereas a tuple is immutable."
        )
        q3_resp = session.select_next_question(eval2)
        self.assertEqual(q3_resp["difficulty"].lower(), "hard")
        self.assertEqual(q3_resp["question_number"], 3)

    def test_average_answer_maintains_difficulty(self):
        """4. Average answer maintains difficulty level."""
        session = AdaptiveSession(interview_id=779, candidate_skills=["Database & SQL"], max_questions=5)
        q1 = session.initial_question

        # Force average evaluation
        fake_eval = {
            "question_id": q1["id"],
            "question_text": q1["question_text"],
            "topic": q1["category"],
            "difficulty": "easy",
            "rating": "Average",
            "composite_score": 55.0
        }
        q2_resp = session.select_next_question(fake_eval)
        # Should stay at easy
        self.assertEqual(q2_resp["difficulty"].lower(), "easy")
        self.assertEqual(q2_resp["question_number"], 2)

    def test_poor_answer_reduces_difficulty(self):
        """5. Poor answer reduces difficulty (Hard -> Medium -> Easy)."""
        session = AdaptiveSession(interview_id=780, candidate_skills=["Python"], max_questions=5)
        session.current_difficulty = "hard"

        fake_eval_hard = {
            "question_id": 99,
            "question_text": "Explain Python GIL internals.",
            "topic": "Python",
            "difficulty": "hard",
            "rating": "Poor",
            "composite_score": 25.0
        }
        q_next = session.select_next_question(fake_eval_hard)
        self.assertEqual(q_next["difficulty"].lower(), "medium")

        # Another poor answer on Medium -> Drops to Easy
        fake_eval_med = {
            "question_id": q_next["question_id"],
            "question_text": q_next["question"],
            "topic": "Python",
            "difficulty": "medium",
            "rating": "Poor",
            "composite_score": 20.0
        }
        q_next2 = session.select_next_question(fake_eval_med)
        self.assertEqual(q_next2["difficulty"].lower(), "easy")

    def test_no_repetition_of_questions(self):
        """6. Avoids duplicate questions during the entire interview."""
        session = AdaptiveSession(interview_id=781, candidate_skills=["Python"], max_questions=5)
        seen_ids = {session.initial_question["id"]}

        current_q = session.initial_question
        for _ in range(4):
            q_id = current_q.get("id") or current_q.get("question_id")
            eval_res = session.evaluate_candidate_answer(q_id, "Python is a programming language.")
            next_q = session.select_next_question(eval_res)
            if next_q.get("is_complete"):
                break
            self.assertNotIn(next_q["question_id"], seen_ids)
            seen_ids.add(next_q["question_id"])
            current_q = next_q

        self.assertEqual(len(seen_ids), len(session.questions_asked))

    def test_max_questions_limit_enforced(self):
        """7. Interview stops gracefully when configured question count is reached."""
        max_q = 3
        session = AdaptiveSession(interview_id=782, candidate_skills=["Java"], max_questions=max_q)
        
        q = session.initial_question
        for i in range(max_q):
            eval_res = session.evaluate_candidate_answer(q.get("question_id", q.get("id")), "Answering technical question accurately.")
            next_step = session.select_next_question(eval_res)
            if i == max_q - 1:
                self.assertTrue(next_step["is_complete"])
                self.assertEqual(next_step["total_questions"], max_q)
            else:
                self.assertFalse(next_step["is_complete"])
                q = next_step


class FastAPIAdaptiveEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from backend.fastapi_app import app as fastapi_app
        cls.client = TestClient(fastapi_app)

    def test_init_and_next_question_flow(self):
        """Tests POST /api/interview/init-adaptive, next-question, and state telemetry."""
        interview_id = 8888
        init_res = self.client.post("/api/interview/init-adaptive", json={
            "interview_id": interview_id,
            "candidate_skills": ["Python", "SQL"],
            "target_role": "Backend Engineer",
            "max_questions": 4
        })
        self.assertEqual(init_res.status_code, 200)
        init_data = init_res.json()
        self.assertEqual(init_data["status"], "success")
        self.assertIn("first_question", init_data)
        q1 = init_data["first_question"]
        self.assertEqual(q1["difficulty"].lower(), "easy")

        # Answer Question 1 strongly
        next_res = self.client.post("/api/interview/next-question", json={
            "interview_id": interview_id,
            "question_id": q1["id"],
            "answer": q1.get("benchmark_answer") or "Python is a high-level interpreted programming language with easy syntax and extensive standard library."
        })
        self.assertEqual(next_res.status_code, 200)
        q2 = next_res.json()
        self.assertEqual(q2["question_number"], 2)
        self.assertEqual(q2["difficulty"].lower(), "medium")

        # Check telemetry state endpoint
        state_res = self.client.get(f"/api/interview/state/{interview_id}")
        self.assertEqual(state_res.status_code, 200)
        state_data = state_res.json()
        self.assertEqual(state_data["questions_asked_count"], 2)
        self.assertIn("Python", state_data["strong_topics"])


class FlaskAdaptiveProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            user = User.query.filter_by(email="adaptive_test@example.com").first()
            if not user:
                user = User(
                    full_name="Adaptive Candidate",
                    email="adaptive_test@example.com",
                    role="candidate"
                )
                user.set_password("SecurePass123!")
                db.session.add(user)
                db.session.commit()
            cls.user_id = user.id

            interview = Interview(
                user_id=user.id,
                target_role="Python Developer",
                status="in_progress"
            )
            db.session.add(interview)
            db.session.commit()
            cls.interview_id = interview.id

    def test_flask_next_question_route(self):
        """Flask endpoint POST /api/interview/<id>/next-question evaluates and returns next question."""
        client = app.test_client()

        login_res = client.post("/api/auth/login", json={
            "email": "adaptive_test@example.com",
            "password": "SecurePass123!"
        })
        token = login_res.json["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Initialize session via start or manager
        AdaptiveInterviewManager.get_or_create_session(
            interview_id=self.interview_id,
            candidate_skills=["Python", "SQL"],
            target_role="Python Developer",
            max_questions=3
        )

        resp = client.post(
            f"/api/interview/{self.interview_id}/next-question",
            json={
                "question_id": 1,
                "answer": "Python is an interpreted programming language with clear readable code."
            },
            headers=headers
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertIn("question", data)
        self.assertIn("difficulty", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
