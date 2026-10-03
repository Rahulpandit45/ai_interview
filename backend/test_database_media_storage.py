import os
import sys
import io
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.services.database import db
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.interview import Interview, InterviewResponse, InterviewMedia
from backend.models.report import Report
from backend.utils.security import generate_token
from backend.config import Config

class DatabaseMediaStorageTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            # Get or create candidate
            self.user = User.query.filter_by(email="mediatest@interview.ai").first()
            if not self.user:
                self.user = User(
                    candidate_id=User.generate_candidate_id(),
                    full_name="Media Test Candidate",
                    email="mediatest@interview.ai",
                    role="candidate",
                    target_role="Software Engineer"
                )
                self.user.set_password("candidate123")
                db.session.add(self.user)
                db.session.commit()
            
            # Ensure candidate has a verified resume for starting an interview
            resume = Resume.query.filter_by(user_id=self.user.id).first()
            if not resume:
                resume = Resume(
                    user_id=self.user.id,
                    filename="Media_Test_Resume.pdf",
                    file_path="resumes/Media_Test_Resume.pdf",
                    candidate_name="Media Test Candidate",
                    is_verified=True,
                    verification_status="verified",
                    screening_score=88.0
                )
                db.session.add(resume)
                db.session.commit()
            else:
                resume.is_verified = True
                resume.verification_status = "verified"
                resume.file_path = resume.file_path or "resumes/Media_Test_Resume.pdf"
                db.session.commit()

            self.token = generate_token(self.user.id, role="candidate")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_01_submit_response_with_media_saves_to_db(self):
        with self.app.app_context():
            # Start interview
            res_start = self.client.post("/api/interview/start", json={"target_role": "Python Backend Engineer"}, headers=self.headers)
            self.assertEqual(res_start.status_code, 201)
            interview_id = res_start.get_json()["data"]["interview_id"]

            # Snapshot count of files in recordings directory before upload
            rec_folder = Config.RECORDING_UPLOAD_FOLDER
            initial_files = set(os.listdir(rec_folder)) if os.path.exists(rec_folder) else set()

            # Create mock binary media (e.g. webm video payload)
            mock_video_bytes = b"\x1a\x45\xdf\xa3" + (b"DATABASE_STORED_WEBM_VIDEO_PAYLOAD_CHUNKS" * 25) # > 1KB
            data = {
                "question_id": "1",
                "question_text": "Describe your experience with scalable web architectures and relational databases.",
                "transcript": "I designed microservices with PostgreSQLBYTEA for direct media persistence without ephemeral disk loss.",
                "recording": (io.BytesIO(mock_video_bytes), "candidate_q1_video.webm")
            }

            res = self.client.post(
                f"/api/interview/{interview_id}/response",
                data=data,
                content_type="multipart/form-data",
                headers=self.headers
            )
            self.assertEqual(res.status_code, 200)
            res_json = res.get_json()
            self.assertEqual(res_json["status"], "success")

            # Check that InterviewMedia record exists in the database
            media_item = InterviewMedia.query.filter_by(interview_id=interview_id).first()
            self.assertIsNotNone(media_item, "InterviewMedia must be saved directly in the database")
            self.assertEqual(media_item.candidate_id, self.user.candidate_id)
            self.assertEqual(media_item.user_id, self.user.id)
            self.assertEqual(media_item.media_type, "video")
            self.assertEqual(media_item.file_name, "candidate_q1_video.webm")
            self.assertEqual(media_item.data, mock_video_bytes)
            self.assertEqual(media_item.file_size, len(mock_video_bytes))

            # Verify no new files remained on the local recordings folder
            if os.path.exists(rec_folder):
                current_files = set(os.listdir(rec_folder))
                new_files = current_files - initial_files
                self.assertEqual(len(new_files), 0, f"Expected 0 persistent local recording files, but found: {new_files}")

            # Test 02: Stream full media (HTTP 200) via /api/interview/<id>/media
            stream_res = self.client.get(f"/api/interview/{interview_id}/media")
            self.assertEqual(stream_res.status_code, 200)
            self.assertEqual(stream_res.data, mock_video_bytes)
            self.assertIn("Accept-Ranges", stream_res.headers)
            self.assertEqual(stream_res.headers["Accept-Ranges"], "bytes")

            # Test 03: Stream partial media (HTTP 206 Range Request) for HTML5 video seeking
            range_headers = {"Range": "bytes=0-49"}
            range_res = self.client.get(f"/api/interview/{interview_id}/media", headers=range_headers)
            self.assertEqual(range_res.status_code, 206)
            self.assertEqual(range_res.data, mock_video_bytes[0:50])
            self.assertIn(f"bytes 0-49/{len(mock_video_bytes)}", range_res.headers.get("Content-Range", ""))

            # Test 04: Fetch by media ID directly
            media_id_res = self.client.get(f"/api/interview/media/{media_item.id}")
            self.assertEqual(media_id_res.status_code, 200)
            self.assertEqual(media_id_res.data, mock_video_bytes)

            # Test 05: Fetch by response ID
            resp_id_res = self.client.get(f"/api/interview/response/{media_item.response_id}/media")
            self.assertEqual(resp_id_res.status_code, 200)
            self.assertEqual(resp_id_res.data, mock_video_bytes)

            # Test 06: Finalize interview and generate report
            fin_res = self.client.post(f"/api/interview/{interview_id}/finish", headers=self.headers)
            self.assertEqual(fin_res.status_code, 200)
            report_data = fin_res.get_json()["report"]
            self.assertEqual(report_data["recording_url"], f"/api/interview/{interview_id}/media")

            # Test 07: Media metadata list endpoint
            list_res = self.client.get(f"/api/interview/{interview_id}/media-list")
            self.assertEqual(list_res.status_code, 200)
            list_json = list_res.get_json()
            self.assertGreaterEqual(len(list_json["media"]), 1)
            self.assertEqual(list_json["media"][0]["file_name"], "candidate_q1_video.webm")
            self.assertEqual(list_json["media"][0]["media_url"], f"/api/interview/media/{media_item.id}")

if __name__ == "__main__":
    unittest.main()
