"""
proctoring_service.py
Real-time AI proctoring service enforcing multi-person presence detection.

Rules & Flow:
1. Normal Condition:
   - 1 face = registered candidate -> continue interview normally.
2. First Violation:
   - Another face (>= 2 faces) detected continuously for confirmation period (default 2.5s, configurable 2-3s):
     -> Give Warning 1.
     -> Message: "⚠️ Warning 1: Another person has been detected. Please ensure you are alone during the interview."
3. Face Leaves:
   - If other face leaves (faces <= 1):
     -> Clear warning, continue interview normally.
4. Second Violation:
   - Another face appears again (>= 2 faces) continuously for confirmation period:
     -> Give Final Warning.
     -> Message: "⚠️ Final Warning: Another person has been detected again. Please ensure you are alone."
5. Persistent Violation (Termination):
   - If other face does not leave within 10 seconds after final warning:
     -> Automatically terminate the interview.
     -> Save violation to database.
     -> Message: "❌ Interview Terminated: Another person remained present after the final warning."
     -> Prevent candidate from continuing.
"""

import os
import sys
import time
import base64
import numpy as np
import cv2
from datetime import datetime
from backend.utils.helpers import utc_now

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Global Cascade Classifier instance for face detection
_face_cascade = None

def get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        local_path = os.path.join(BASE_DIR, "trained_models", "haarcascade_frontalface_default.xml")
        if os.path.exists(local_path):
            _face_cascade = cv2.CascadeClassifier(local_path)
        else:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if not os.path.exists(cascade_path):
                cascade_path = os.path.join(os.path.dirname(cv2.__file__), "data", "haarcascade_frontalface_default.xml")
            if os.path.exists(cascade_path):
                _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def detect_faces_in_image(image_bytes: bytes) -> int:
    """
    Decodes raw image bytes and detects the number of human faces using OpenCV.
    Returns integer count of detected faces.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return 1

        cascade = get_face_cascade()
        if cascade is None or cascade.empty():
            return 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Equalize histogram for robustness in varied webcam lighting
        gray = cv2.equalizeHist(gray)
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=3,
            minSize=(30, 30)
        )
        return max(1, len(faces)) if len(faces) <= 1 else len(faces)
    except Exception as e:
        print(f"[Proctoring CV Error] {e}")
        return 1


class ProctoringConfig:
    def __init__(
        self,
        confirmation_seconds: float = None,
        final_warning_timeout_seconds: float = None,
        allowed_candidate_faces: int = 1
    ):
        # Allow environment variable overrides or parameters
        env_confirm = os.environ.get("PROCTORING_CONFIRMATION_SECONDS")
        env_timeout = os.environ.get("PROCTORING_FINAL_TIMEOUT_SECONDS")

        self.confirmation_seconds = (
            confirmation_seconds if confirmation_seconds is not None
            else (float(env_confirm) if env_confirm else 2.5)
        )
        self.final_warning_timeout_seconds = (
            final_warning_timeout_seconds if final_warning_timeout_seconds is not None
            else (float(env_timeout) if env_timeout else 10.0)
        )
        self.allowed_candidate_faces = allowed_candidate_faces


class InterviewProctoringSession:
    """
    Tracks state machine transitions for an active interview session.
    """
    def __init__(self, interview_id: int, config: ProctoringConfig = None):
        self.interview_id = interview_id
        self.config = config or ProctoringConfig()
        
        # State tracking
        self.warning_count = 0  # 0, 1, 2
        self.status = "clean"   # "clean", "warning_1", "warning_cleared", "final_warning", "terminated"
        self.is_terminated = False
        self.termination_reason = None
        
        # Timing trackers (in fractional epoch seconds)
        self.other_face_continuous_start = None  # When >=2 faces continuous window began
        self.final_warning_issued_time = None    # When final warning was triggered
        self.last_check_time = None
        self.last_faces_count = 1

    def evaluate_faces(self, faces_detected: int, current_time: float = None) -> dict:
        """
        Processes a face count event and advances the proctoring state machine.
        """
        now = current_time if current_time is not None else time.time()
        self.last_check_time = now
        self.last_faces_count = faces_detected

        # If already terminated, retain terminal state
        if self.is_terminated:
            return {
                "interview_id": self.interview_id,
                "status": "terminated",
                "warning_count": self.warning_count,
                "faces_detected": faces_detected,
                "additional_faces": max(0, faces_detected - self.config.allowed_candidate_faces),
                "message": "❌ Interview Terminated: Another person remained present after the final warning.",
                "is_terminated": True,
                "remaining_seconds": 0.0
            }

        has_additional_face = faces_detected > self.config.allowed_candidate_faces

        # Case 1: Normal condition or other face has left (faces <= 1)
        if not has_additional_face:
            # Reset the continuous violation timer
            self.other_face_continuous_start = None
            
            # If we were previously showing a warning, clear it
            if self.status in ["warning_1", "final_warning"]:
                self.status = "warning_cleared"
                message = "The other person has left. You may continue your interview normally."
                # Note: self.final_warning_issued_time reset so countdown stops
                self.final_warning_issued_time = None
            else:
                self.status = "clean"
                message = "Normal: Registered candidate verified alone."

            return {
                "interview_id": self.interview_id,
                "status": self.status,
                "warning_count": self.warning_count,
                "faces_detected": faces_detected,
                "additional_faces": 0,
                "message": message,
                "is_terminated": False,
                "remaining_seconds": None
            }

        # Case 2: Additional face detected (faces >= 2)
        # Start or continue tracking the continuous presence duration
        if self.other_face_continuous_start is None:
            self.other_face_continuous_start = now

        continuous_duration = now - self.other_face_continuous_start

        # Check if already in Final Warning state -> Evaluate 10s termination countdown
        if self.warning_count >= 2 and self.final_warning_issued_time is not None:
            time_in_final_warning = now - self.final_warning_issued_time
            remaining = max(0.0, self.config.final_warning_timeout_seconds - time_in_final_warning)

            if time_in_final_warning >= self.config.final_warning_timeout_seconds:
                # Persistent second violation -> Terminate!
                self.is_terminated = True
                self.status = "terminated"
                self.termination_reason = "Another person remained present after the final warning."
                self._persist_db_event("terminated", faces_detected, self.termination_reason)

                return {
                    "interview_id": self.interview_id,
                    "status": "terminated",
                    "warning_count": 2,
                    "faces_detected": faces_detected,
                    "additional_faces": faces_detected - 1,
                    "message": "❌ Interview Terminated: Another person remained present after the final warning.",
                    "is_terminated": True,
                    "remaining_seconds": 0.0
                }

            # Still in countdown before 10s limit
            return {
                "interview_id": self.interview_id,
                "status": "final_warning",
                "warning_count": 2,
                "faces_detected": faces_detected,
                "additional_faces": faces_detected - 1,
                "message": "⚠️ Final Warning: Another person has been detected again. Please ensure you are alone.",
                "is_terminated": False,
                "remaining_seconds": round(remaining, 1)
            }

        # Check if continuous presence satisfies the confirmation window (e.g. 2.5s)
        if continuous_duration < self.config.confirmation_seconds:
            # Brief / momentary detection error -> Ignore, do not issue warning yet
            return {
                "interview_id": self.interview_id,
                "status": self.status if self.status in ["warning_1", "final_warning"] else "clean",
                "warning_count": self.warning_count,
                "faces_detected": faces_detected,
                "additional_faces": faces_detected - 1,
                "message": f"Analyzing frame ({round(continuous_duration, 1)}s / {self.config.confirmation_seconds}s confirmation window)...",
                "is_terminated": False,
                "remaining_seconds": None
            }

        # Confirmation period reached!
        # Evaluate whether this is Violation 1 or Violation 2
        if self.warning_count == 0:
            # First Violation -> Warning 1
            self.warning_count = 1
            self.status = "warning_1"
            msg = "⚠️ Warning 1: Another person has been detected. Please ensure you are alone during the interview."
            self._persist_db_event("warning_1", faces_detected, msg)

            return {
                "interview_id": self.interview_id,
                "status": "warning_1",
                "warning_count": 1,
                "faces_detected": faces_detected,
                "additional_faces": faces_detected - 1,
                "message": msg,
                "is_terminated": False,
                "remaining_seconds": None
            }

        elif self.warning_count == 1:
            # Second Violation -> Final Warning
            self.warning_count = 2
            self.status = "final_warning"
            self.final_warning_issued_time = now
            msg = "⚠️ Final Warning: Another person has been detected again. Please ensure you are alone."
            self._persist_db_event("final_warning", faces_detected, msg)

            remaining = self.config.final_warning_timeout_seconds
            return {
                "interview_id": self.interview_id,
                "status": "final_warning",
                "warning_count": 2,
                "faces_detected": faces_detected,
                "additional_faces": faces_detected - 1,
                "message": msg,
                "is_terminated": False,
                "remaining_seconds": round(remaining, 1)
            }

        return {
            "interview_id": self.interview_id,
            "status": self.status,
            "warning_count": self.warning_count,
            "faces_detected": faces_detected,
            "additional_faces": faces_detected - 1,
            "message": "Monitoring session...",
            "is_terminated": False,
            "remaining_seconds": None
        }

    def _persist_db_event(self, warning_level: str, faces_detected: int, message: str):
        """Persists violation record and updates interview status in database."""
        try:
            from backend.app import app
            with app.app_context():
                from backend.services.database import db
                from backend.models.interview import Interview, ProctoringViolation
                interview = db.session.get(Interview, self.interview_id)
                if interview:
                    interview.warning_count = self.warning_count
                    interview.detected_faces_count = faces_detected
                    interview.last_face_detection_time = utc_now()
                    interview.proctoring_status = self.status
                    if self.is_terminated:
                        interview.status = "terminated"
                        interview.termination_reason = self.termination_reason

                    violation = ProctoringViolation(
                        interview_id=self.interview_id,
                        timestamp=utc_now(),
                        faces_detected=faces_detected,
                        warning_level=warning_level,
                        message=message
                    )
                    db.session.add(violation)
                    db.session.commit()
        except Exception as e:
            print(f"[Proctoring DB Persist Warning] {e}")


class ProctoringManager:
    """
    Singleton manager maintaining active interview proctoring sessions.
    """
    _sessions = {}

    @classmethod
    def get_session(cls, interview_id: int, config: ProctoringConfig = None) -> InterviewProctoringSession:
        if interview_id not in cls._sessions:
            cls._sessions[interview_id] = InterviewProctoringSession(interview_id, config=config)
        elif config is not None:
            cls._sessions[interview_id].config = config
        return cls._sessions[interview_id]

    @classmethod
    def reset_session(cls, interview_id: int):
        if interview_id in cls._sessions:
            del cls._sessions[interview_id]

    @classmethod
    def process_check(
        cls,
        interview_id: int,
        faces_detected: int = None,
        frame_bytes: bytes = None,
        frame_base64: str = None,
        current_time: float = None,
        config: ProctoringConfig = None
    ) -> dict:
        session = cls.get_session(interview_id, config=config)

        # Determine face count:
        raw_image_data = None
        if faces_detected is None:
            if frame_base64:
                # Strip data URI header if present
                if "," in frame_base64:
                    frame_base64 = frame_base64.split(",", 1)[1]
                decoded_bytes = base64.b64decode(frame_base64)
                raw_image_data = decoded_bytes
                faces_detected = detect_faces_in_image(decoded_bytes)
            elif frame_bytes:
                raw_image_data = frame_bytes
                faces_detected = detect_faces_in_image(frame_bytes)
            else:
                faces_detected = 1
        elif frame_base64 or frame_bytes:
            if frame_base64:
                b64_clean = frame_base64.split(",", 1)[1] if "," in frame_base64 else frame_base64
                try:
                    raw_image_data = base64.b64decode(b64_clean)
                except Exception:
                    raw_image_data = None
            else:
                raw_image_data = frame_bytes

        # Automatically capture first clean interview snapshot if not already saved
        if faces_detected == 1 and raw_image_data:
            try:
                from backend.app import app
                with app.app_context():
                    from backend.services.database import db
                    from backend.models.interview import Interview
                    from backend.config import Config
                    interview = db.session.get(Interview, interview_id)
                    if interview and not interview.interview_photo:
                        os.makedirs(Config.PROFILE_UPLOAD_FOLDER, exist_ok=True)
                        snap_name = f"interview_snap_{interview_id}.jpg"
                        snap_path = os.path.join(Config.PROFILE_UPLOAD_FOLDER, snap_name)
                        with open(snap_path, "wb") as f:
                            f.write(raw_image_data)
                        interview.interview_photo = f"profiles/{snap_name}"
                        db.session.commit()
            except Exception as e:
                print(f"[Interview Snapshot Warning] {e}")

        return session.evaluate_faces(faces_detected, current_time=current_time)
