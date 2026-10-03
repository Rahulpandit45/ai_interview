import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.services.database import db
from backend.models.user import User
from backend.models.resume import Resume
from backend.utils.security import generate_token

class CandidateSidebarEndpointsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            # Get or create candidate
            self.user = User.query.filter_by(email="rahul@interview.ai").first()
            if not self.user:
                self.user = User(
                    candidate_id=User.generate_candidate_id(),
                    full_name="Rahul Kumar Pandit",
                    email="rahul@interview.ai",
                    role="candidate",
                    target_role="Software Engineer"
                )
                self.user.set_password("candidate123")
                db.session.add(self.user)
                db.session.commit()
            else:
                self.user.set_password("candidate123")
                db.session.commit()

            self.token = generate_token(self.user.id, role="candidate")

    def test_01_update_profile(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "full_name": "jarin",
            "phone": "9846643654",
            "location": "kathmandu",
            "linkedin": "https://shorturl.at/LdHgO",
            "github": "https://github.com/Nirajmalla123",
            "education": "Be.computer",
            "experience": "1 year as Frontend Developer",
            "target_role": "Software Engineer"
        }
        res = self.client.put("/api/auth/profile", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["user"]["full_name"], "jarin")
        self.assertEqual(data["user"]["phone"], "9846643654")
        self.assertEqual(data["user"]["location"], "kathmandu")
        self.assertEqual(data["user"]["linkedin"], "https://shorturl.at/LdHgO")
        self.assertEqual(data["user"]["github"], "https://github.com/Nirajmalla123")
        self.assertEqual(data["user"]["education"], "Be.computer")
        self.assertEqual(data["user"]["experience"], "1 year as Frontend Developer")
        self.assertEqual(data["user"]["target_role"], "Software Engineer")

    def test_02_change_password(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Wrong current password
        res_wrong = self.client.put("/api/auth/password", json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }, headers=headers)
        self.assertEqual(res_wrong.status_code, 400)

        # Correct current password
        res_ok = self.client.put("/api/auth/password", json={
            "current_password": "candidate123",
            "new_password": "candidateNew456"
        }, headers=headers)
        self.assertEqual(res_ok.status_code, 200)

        # Reset back
        res_reset = self.client.put("/api/auth/password", json={
            "current_password": "candidateNew456",
            "new_password": "candidate123"
        }, headers=headers)
        self.assertEqual(res_reset.status_code, 200)

    def test_03_resume_download_and_view(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.app.app_context():
            # Check if user has a resume file, or create mock for testing
            resume = Resume.query.filter_by(user_id=self.user.id).first()
            if not resume or not os.path.exists(resume.file_path):
                mock_path = os.path.join(self.app.config["RESUME_UPLOAD_FOLDER"], "sample_test_resume.txt")
                with open(mock_path, "w") as f:
                    f.write("Rahul Kumar Pandit\nSoftware Engineer\nSkills: Python, FastAPI")
                if not resume:
                    resume = Resume(
                        user_id=self.user.id,
                        filename="sample_test_resume.txt",
                        file_path=mock_path,
                        candidate_name="Rahul Kumar Pandit",
                        is_verified=True,
                        screening_score=88.5
                    )
                    db.session.add(resume)
                else:
                    resume.file_path = mock_path
                    resume.filename = "sample_test_resume.txt"
                db.session.commit()

        # Test download endpoint
        res_dl = self.client.get("/api/resume/download", headers=headers)
        self.assertEqual(res_dl.status_code, 200)
        self.assertIn("attachment", res_dl.headers.get("Content-Disposition", ""))

        # Test view endpoint
        res_view = self.client.get("/api/resume/view", headers=headers)
        self.assertEqual(res_view.status_code, 200)

if __name__ == "__main__":
    unittest.main()
