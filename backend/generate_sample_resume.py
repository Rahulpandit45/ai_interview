"""
generate_sample_resume.py
Generates a realistic sample resume text and PDF for candidate Rahul Kumar Pandit
to demonstrate resume parsing and screening.
"""

import os
from pypdf import PdfWriter

SAMPLE_RESUME_TEXT = """
Rahul Kumar Pandit
Email: rahul@interview.ai | Phone: +977-9812345678 | Kathmandu, Nepal
Portfolio: github.com/rahulkumar | LinkedIn: linkedin.com/in/rahulkumar

PROFESSIONAL SUMMARY
Dynamic Computer Engineer with 2+ years of experience in software development, machine learning, 
and full-stack web applications. Proven expertise in designing scalable RESTful APIs, computer vision 
pipelines, and distributed microservices.

EDUCATION
Bachelor of Computer Engineering (B.E.)
Mid-West University, Graduate School of Engineering, Surkhet, Nepal | Graduated: 2025
Key Coursework: Data Structures, Algorithms, Artificial Intelligence, Database Management Systems, Computer Networks

TECHNICAL SKILLS
- Programming: Python, C++, JavaScript, SQL, HTML, CSS
- Frameworks & Libraries: Flask, PyTorch, OpenCV, MediaPipe, NumPy, Pandas, Scikit-Learn, Transformers
- Databases & Tools: MySQL, PostgreSQL, Docker, Git, Linux, REST API

PROJECT EXPERIENCE
AI-Powered Video Interview Assessment System
- Developed end-to-end interview assessment platform using Flask, PyTorch, and OpenCV.
- Implemented real-time face landmark tracking, eye contact analysis, and head pose estimation.
- Integrated Whisper speech recognition and Sentence-Transformers for candidate semantic answer scoring.

Distributed Microservices API Platform
- Architected RESTful microservices with Python, Flask, and MySQL, achieving 99.9% uptime.
- Containerized applications using Docker and set up automated CI/CD deployment pipelines.

SOFT SKILLS
Communication, Problem Solving, Teamwork, Leadership, Time Management, Critical Thinking
"""

def create_sample_resume():
    sample_dir = os.path.join(os.path.dirname(__file__), "uploads", "resumes")
    os.makedirs(sample_dir, exist_ok=True)
    
    txt_path = os.path.join(sample_dir, "sample_resume_rahul.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_RESUME_TEXT.strip())
        
    print(f"[Sample Resume] Created sample text resume at: {txt_path}")
    return txt_path

if __name__ == "__main__":
    create_sample_resume()
