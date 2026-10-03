# AI-Powered Intelligent Video Interview Assessment System Using Deep Learning and Computer Vision

Final Year Computer Engineering Project
Mid-West University, Graduate School of Engineering, Surkhet, Nepal

---

## 1. Project Overview

Traditional recruitment and interview processes are often time-consuming, subjective, and prone to unconscious human bias. This platform provides an intelligent, automated, and **locally deployable** video interview assessment system that:
1. Registers and authenticates candidates and recruiters.
2. Extracts and analyzes resume data (name, education, technical & soft skills, experience) from PDF/DOCX files.
3. Automatically screens candidate resumes and computes role relevance scores using NLP sentence embeddings.
4. Generates personalized, adaptive interview questions across General, Technical, Behavioral, and Communication categories.
5. Conducts webcam and microphone-based video interviews with live face-landmark mesh tracking and audio level visualization.
6. Transcribes spoken responses locally using **OpenAI Whisper**.
7. Analyzes semantic response relevance, technical vocabulary depth, and completeness using **Sentence-Transformers (BERT)**.
8. Measures Computer Vision behavioral telemetry (eye-contact consistency, head stability/pose, and facial expressiveness) via **OpenCV & MediaPipe**.
9. Fuses text, audio, and video signals into a 10-dimensional multimodal feature vector.
10. Predicts Communication, Technical, Confidence, and Overall scores (0–100) using a trained **Random Forest Multimodal Scoring Model**.
11. Generates comprehensive visual assessment reports with radial score gauges, section breakdowns, strengths, areas for improvement, and personalized feedback.
12. Delivers candidate and recruiter/admin dashboards with applicant ranking and search.

> [!NOTE]
> **Zero External AI API Dependencies**: The entire AI inference pipeline runs 100% locally on the host machine using open-source models without requiring paid external API subscriptions (e.g. OpenAI or Anthropic).

---

## 2. System Architecture

```
[Candidate Browser (HTML5/CSS3/JS)]
   │
   ├─► 1. Authentication (JWT / Session)
   ├─► 2. Resume Upload & Parsing (PyPDF + Regex + NLP)
   ├─► 3. Resume Screening (Sentence-Transformers all-MiniLM-L6-v2)
   ├─► 4. Question Generator (Adaptive Skill-based generation)
   ├─► 5. Webcam Video Interview (MediaRecorder + MediaPipe Canvas)
   │
[Flask REST Backend (Python 3.13)]
   │
   ├──► 5.1 Speech Recognition (OpenAI Whisper 'tiny' / 'base')
   ├──► 5.2 NLP Semantic Analysis (Sentence-Transformers / BERT Cosine Similarity)
   ├──► 5.3 Computer Vision (OpenCV + MediaPipe 3D Face Landmarker)
   │
   └──► 6. Multimodal Feature Fusion Layer (10D Unified Vector)
            │
            ▼
        7. AI Scoring Model (Random Forest / MLP Ensemble)
            │
            ▼
        8. Assessment Report & Recruiter Console (Scores, Strengths, Feedback, Ranking)
```

---

## 3. Project Directory Structure

```
e:/project/
├── run.py                          # Root convenience launcher
├── README.md                       # Complete project documentation
│
├── frontend/                       # Frontend Application
│   ├── index.html                  # Landing page
│   ├── login.html                  # Authentication login page (Candidate & Admin portals)
│   ├── register.html               # Registration page with live camera portrait & OTP
│   ├── dashboard.html              # Candidate workspace & overview
│   ├── resume_upload.html          # Resume upload & NLP screening view
│   ├── interview.html              # Live webcam interview room
│   ├── report.html                 # Comprehensive AI assessment report
│   ├── candidate_report.html       # Official printable candidate dossier
│   ├── admin.html                  # Institutional Administrator & Talent console
│   ├── db_viewer.html              # SQLite database records explorer
│   ├── qa_test.html                # IT Q&A knowledge engine testing console
│   ├── css/
│   │   └── style.css               # Dark glassmorphism design system
│   ├── js/
│   │   ├── main.js                 # API client, toast notifications, auth state
│   │   ├── auth.js                 # Login & registration forms
│   │   ├── interview.js            # Question sequencer, TTS reader, submission
│   │   └── webcam.js               # MediaRecorder, canvas face mesh HUD
│   └── assets/
│       ├── images/
│       └── icons/
│
└── backend/                        # Backend Application
    ├── app.py                      # Flask main entry point & static server
    ├── config.py                   # Configuration parameters
    ├── requirements.txt            # Dependency list
    ├── database_schema.sql         # Pure MySQL DDL schema
    ├── fetch_models.py             # Automatic model download & training script
    ├── test_pipeline.py            # Automated 10-step integration test suite
    ├── generate_sample_resume.py   # Sample candidate resume generator
    │
    ├── routes/
    │   ├── auth_routes.py          # /api/auth/register, /login, /me, /logout
    │   ├── resume_routes.py        # /api/resume/upload, /parsed, /screen
    │   ├── interview_routes.py     # /api/interview/start, /response, /finish
    │   ├── report_routes.py        # /api/reports/<id>, /my-reports
    │   └── admin_routes.py         # /api/admin/stats, /candidates, /candidate/<id>
    │
    ├── models/
    │   ├── user.py                 # User model (candidate & recruiter)
    │   ├── resume.py               # Resume model with JSON skills
    │   ├── question.py             # Question model with default seedings
    │   ├── interview.py            # Interview & InterviewResponse models
    │   └── report.py               # Report model with multimodal scores & feedback
    │
    ├── services/
    │   ├── database.py             # SQLAlchemy setup (MySQL + SQLite fallback)
    │   ├── resume_service.py       # Resume parsing & screening coordinator
    │   ├── interview_service.py    # Interview session manager
    │   └── report_service.py       # Report & recruiter ranking services
    │
    ├── ai/
    │   ├── resume/
    │   │   ├── parser.py           # PyPDF text & entity extraction
    │   │   └── screening.py        # Sentence-Transformer relevance matcher
    │   ├── nlp/
    │   │   ├── question_generator.py # Dynamic category-based question generator
    │   │   └── response_analyzer.py  # BERT semantic similarity & technical depth
    │   ├── speech/
    │   │   └── whisper_transcriber.py# OpenAI Whisper transcription & WPM
    │   ├── vision/
    │   │   ├── face_detection.py   # OpenCV face visibility detection
    │   │   ├── eye_contact.py      # Eye contact and gaze consistency
    │   │   ├── head_pose.py        # Head stability & movement estimation
    │   │   └── facial_expression.py# Facial engagement features & limitations
    │   └── scoring/
    │       ├── feature_fusion.py   # Multimodal 10D feature vector builder
    │       └── final_score.py      # Random Forest score predictor & feedback
    │
    ├── trained_models/             # Stored local deep learning model weights
    │   ├── face_landmarker.task    # MediaPipe Face Landmarker
    │   └── multimodal_scoring_rf.pkl# Trained multimodal scoring model
    │
    ├── uploads/
    │   ├── resumes/                # Uploaded candidate CVs
    │   └── recordings/             # Uploaded webcam audio/video files
    └── utils/
        ├── security.py             # JWT token helpers & decorators
        └── helpers.py              # File validation & FFmpeg conversion
```

---

## 4. Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.13 + Flask 3.1 |
| **Frontend UI** | HTML5, Modern CSS3 (Dark Glassmorphism), JavaScript (ES6) |
| **Database** | MySQL (with zero-configuration local SQLite fallback) |
| **Deep Learning Framework** | PyTorch 2.13 |
| **Computer Vision** | OpenCV 5.0 + Google MediaPipe Face Landmarker |
| **Speech-to-Text** | OpenAI Whisper (Local `tiny` model) + Bundled FFmpeg |
| **NLP & Semantic Similarity** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Scoring Classifier** | Scikit-Learn Random Forest Regressor / Feature Fusion |
| **Data Processing** | NumPy, Pandas, PyPDF, SciPy, SoundFile |

---

## 5. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Windows PowerShell / Command Prompt
- MySQL Server (optional; SQLite fallback is built-in)

### Step 1: Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 2: Fetch and Provision Models
Run the automated model fetcher to download MediaPipe, Sentence-Transformers, Whisper, and train the multimodal scoring model:
```powershell
python backend/fetch_models.py
```

### Step 3: (Optional) MySQL Database Setup
If using MySQL Server:
1. Open MySQL Workbench, phpMyAdmin, or MySQL CLI:
```sql
CREATE DATABASE interview_db;
```
2. Import `backend/database_schema.sql` into `interview_db`.
3. Set environment variables if credentials differ from default `root:root`:
```powershell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_DB="interview_db"
```
*(If MySQL is not started, the system automatically uses `backend/interview_db.sqlite` so you can start testing immediately!)*

### Step 4: Run the Application
```powershell
python run.py
```
Open your browser at:
👉 **`http://localhost:5000`**

---

## 6. Pre-Configured Demo Accounts & Access Control

> [!IMPORTANT]
> **Administrator Access Policy**:
> - Public administrator registration is strictly disabled.
> - Admin accounts are created & provided exclusively by the company or university.
> - Admins can log in **only** using their official **Admin ID** and password (email login is blocked for administrators).
> - New admin accounts can be provisioned via the Admin Console modal or via CLI: `python backend/create_admin.py`.

| Role | Official Identifier | Password | Institution | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate** | `rahul@interview.ai` *(or `CID-2026-9CNH5C`)* | `candidate123` | N/A | Resume screening, live webcam interview, report view |
| **Recruiter/Admin** | **`ADM-2026-001`** *(Official Admin ID)* | `admin123` | Mid-West University | Candidate ranking table, applicant metrics, provisioning |

---

## 7. Automated Testing & Verification

Run the automated test suites:
```powershell
# 1. Core Multimodal AI Pipeline Test Suite
python backend/test_pipeline.py

# 2. Candidate Registration & Photo Storage Suite
python backend/test_candidate_registration.py

# 3. Administrator Access & RBAC Security Suite
python backend/test_admin_access.py
```

### Test Case Verification Summary:
| Test Suite | Focus | Total Tests | Status |
| :--- | :--- | :--- | :--- |
| **Pipeline Suite** | End-to-end multimodal interview & scoring | 11 Tests | **PASSED** (100%) |
| **Candidate Suite** | ID permanence, photo verification, public block | 12 Tests | **PASSED** (100%) |
| **RBAC Suite** | Admin ID login, endpoint guards, provisioning | 20 Tests | **PASSED** (100%) |

---

## 8. Academic & Ethical Considerations

- **Ethical Facial Telemetry**: Facial expression analysis in this system is treated strictly as surface-level geometric model metrics (smile frequency, expressiveness) and NOT as definitive emotional truth.
- **Multimodal Superiority**: As demonstrated in literature (MIT Interview Dataset, 2020), multimodal fusion (Text + Speech + Vision) significantly outperforms single-modality scoring by balancing technical accuracy with communication clarity.
- **Data Privacy**: All video recordings and candidate resumes remain stored securely on the local server without transmitting data to external cloud APIs.
