"""
test_profile_question_model.py
Comprehensive test suite verifying:
1. Question generation based on candidate CV profile and technical skills.
2. Distinct, personalized question tracks for different candidate profiles.
3. 10-stage interview progression.
4. Dynamic follow-up question generation after candidate responses.
5. Full 10-question interview lifecycle and completion.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.ai.nlp.profile_question_model import ProfileQuestionGenerator
from backend.services.adaptive_interview_service import (
    AdaptiveSession,
    AdaptiveInterviewManager
)


class ProfileQuestionModelTests(unittest.TestCase):

    def test_profile_tailored_10_questions(self):
        """1. Generates 10 distinct, relevant questions tailored to the candidate's CV profile."""
        profile = {
            "candidate_name": "Aarav Sharma",
            "technical_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            "experience": "3 years",
            "education": "B.Sc. in Computer Science",
            "projects": "Built high-throughput REST APIs and Redis caching microservice"
        }

        questions = ProfileQuestionGenerator.generate_candidate_questions(
            profile_data=profile,
            target_role="Python Developer",
            count=10
        )

        self.assertEqual(len(questions), 10)
        
        # Verify 10 distinct questions (zero duplicates)
        q_ids = [q["id"] for q in questions]
        self.assertEqual(len(set(q_ids)), 10)

        # Verify progression from easy to hard
        diffs = [q["difficulty"].lower() for q in questions]
        self.assertIn(diffs[0], ["easy"])
        self.assertIn(diffs[1], ["easy", "medium"])
        self.assertIn(diffs[-1], ["hard", "medium"])

        # Verify domain relevance
        categories = [q["category"].lower() for q in questions]
        has_relevant_category = any(
            any(skill.lower() in cat for skill in ["python", "sql", "database", "programming", "cloud", "docker"])
            for cat in categories
        )
        self.assertTrue(has_relevant_category)

    def test_different_questions_for_different_candidates(self):
        """2. Ensures different candidates with different profiles receive different questions."""
        candidate_a = {
            "candidate_name": "Priya Patel",
            "technical_skills": ["JavaScript", "React", "Node.js", "CSS", "TypeScript"],
            "experience": "2 years",
            "education": "B.E. in Information Technology",
            "projects": "Developed interactive frontend dashboards in React"
        }

        candidate_b = {
            "candidate_name": "David Kim",
            "technical_skills": ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD"],
            "experience": "4 years",
            "education": "B.Tech in Computer Engineering",
            "projects": "Managed cloud infrastructure and Kubernetes clusters"
        }

        questions_a = ProfileQuestionGenerator.generate_candidate_questions(
            profile_data=candidate_a,
            target_role="Frontend Engineer",
            count=10
        )

        questions_b = ProfileQuestionGenerator.generate_candidate_questions(
            profile_data=candidate_b,
            target_role="DevOps Engineer",
            count=10
        )

        self.assertEqual(len(questions_a), 10)
        self.assertEqual(len(questions_b), 10)

        texts_a = [q["question_text"] for q in questions_a]
        texts_b = [q["question_text"] for q in questions_b]

        # The question sets must be substantially different and personalized
        overlap = set(texts_a).intersection(set(texts_b))
        self.assertLess(len(overlap), 4, f"Expected high differentiation between candidates, found overlap: {overlap}")

    def test_followup_question_generation_after_answer(self):
        """3. Generates appropriate contextual follow-up questions conditioned on candidate answers."""
        profile = {
            "candidate_name": "Rohan Verma",
            "technical_skills": ["Python", "Flask", "SQL"],
            "experience": "2 years"
        }

        # Follow-up on strong answer
        prev_q = "What is database indexing and how do B-trees improve query speeds?"
        strong_ans = "B-tree indexes maintain balanced sorted trees to provide logarithmic search time for SELECT queries."
        followup_strong, is_f = ProfileQuestionGenerator.generate_followup_question(
            profile_data=profile,
            previous_question=prev_q,
            candidate_answer=strong_ans,
            performance_rating="Good",
            current_difficulty="medium",
            category="Database & SQL"
        )

        self.assertTrue(is_f)
        self.assertIsNotNone(followup_strong.get("question_text"))
        self.assertTrue(len(followup_strong["question_text"]) > 10)
        self.assertTrue("?" in followup_strong["question_text"])

        # Follow-up on average answer
        avg_ans = "It makes queries faster by looking up keys."
        followup_avg, _ = ProfileQuestionGenerator.generate_followup_question(
            profile_data=profile,
            previous_question=prev_q,
            candidate_answer=avg_ans,
            performance_rating="Average",
            current_difficulty="medium",
            category="Database & SQL"
        )
        self.assertIsNotNone(followup_avg.get("question_text"))

    def test_full_10_question_adaptive_session(self):
        """4. Verifies a full 10-question adaptive interview session progresses smoothly to completion."""
        profile = {
            "candidate_name": "Elena Rostova",
            "technical_skills": ["Python", "PostgreSQL", "Docker"],
            "experience": "3 years",
            "target_role": "Backend Engineer"
        }

        session = AdaptiveSession(
            interview_id=9901,
            candidate_skills=profile["technical_skills"],
            target_role=profile["target_role"],
            max_questions=10,
            profile_data=profile
        )

        self.assertEqual(session.max_questions, 10)
        self.assertEqual(len(session.questions_asked), 1)
        self.assertFalse(session.is_complete)

        # Step through 10 questions
        for step in range(1, 11):
            current_q = session.questions_asked[-1]
            eval_res = session.evaluate_candidate_answer(
                current_q["id"],
                f"Candidate answer explaining {current_q.get('category', 'concept')} with technical details and structure."
            )
            next_step = session.select_next_question(eval_res)
            
            if step < 10:
                self.assertFalse(next_step["is_complete"])
                self.assertEqual(next_step["question_number"], step + 1)
            else:
                self.assertTrue(next_step["is_complete"])
                self.assertEqual(next_step["total_questions"], 10)

        self.assertTrue(session.is_complete)
        self.assertEqual(len(session.questions_asked), 10)

        # Ensure all 10 question IDs are unique
        asked_ids = [q["id"] for q in session.questions_asked]
        self.assertEqual(len(asked_ids), len(set(asked_ids)))


if __name__ == "__main__":
    unittest.main()
