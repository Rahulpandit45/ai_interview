import re
import os
from pypdf import PdfReader

TECHNICAL_SKILL_KEYWORDS = [
    "python", "flask", "django", "fastapi", "javascript", "typescript", "react", "angular",
    "vue", "node.js", "express", "html", "css", "sql", "mysql", "postgresql", "mongodb",
    "sqlite", "c", "c++", "java", "c#", "go", "rust", "machine learning", "deep learning",
    "computer vision", "nlp", "natural language processing", "tensorflow", "pytorch",
    "keras", "opencv", "mediapipe", "pandas", "numpy", "scikit-learn", "scipy", "whisper",
    "bert", "transformers", "docker", "kubernetes", "git", "github", "linux", "aws", "azure",
    "gcp", "rest api", "graphql", "redis", "data structures", "algorithms", "oop", "system design"
]

SOFT_SKILL_KEYWORDS = [
    "communication", "leadership", "teamwork", "collaboration", "problem solving",
    "time management", "critical thinking", "adaptability", "work ethic", "creativity",
    "presentation", "interpersonal", "conflict resolution", "mentoring", "negotiation",
    "analytical thinking", "decision making", "emotional intelligence"
]

def extract_text_from_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"[Parser Error] Failed to extract text from PDF: {e}")
    return text.strip()

def extract_text_from_file(file_path):
    ext = file_path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif ext in ["txt", "csv", "log"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        # Fallback raw reading
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

def extract_candidate_name_from_text(raw_text: str) -> str:
    """
    Extracts the candidate's full name from resume text using explicit label matching
    and prominent header analysis.
    """
    # 1. Explicit name prefix check (e.g. "Name: Rahul Pandit", "Candidate: Rahul Pandit")
    prefix_match = re.search(r'(?:full\s+name|candidate\s+name|candidate|name)\s*[:\-]\s*([a-zA-Z\s\.\-]{3,40})', raw_text, re.IGNORECASE)
    if prefix_match:
        candidate_raw = prefix_match.group(1).strip()
        words = candidate_raw.split()
        if 2 <= len(words) <= 5 and not any(w in candidate_raw.lower() for w in ["resume", "curriculum", "vitae", "profile", "software", "developer"]):
            return candidate_raw.title()

    # 2. Inspect first 8 non-empty lines for candidate name header
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    blocked_terms = [
        "resume", "curriculum", "vitae", "cv", "page", "email", "phone", "contact",
        "profile", "summary", "objective", "address", "linkedin", "github", "portfolio",
        "software engineer", "developer", "education", "experience", "skills", "projects"
    ]
    for line in lines[:8]:
        # Skip lines containing email, numbers, or links
        if "@" in line or any(char.isdigit() for char in line) or "http" in line.lower() or "www." in line.lower() or "/" in line:
            continue
        clean_line = re.sub(r'[^a-zA-Z\s]', ' ', line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4:
            line_lower = clean_line.lower()
            if not any(bt in line_lower for bt in blocked_terms):
                return clean_line.title()

    return "Candidate"

def parse_resume(file_path):
    """
    Parses resume document and extracts:
    - candidate_name
    - email
    - phone
    - education
    - experience
    - technical_skills
    - soft_skills
    """
    raw_text = extract_text_from_file(file_path)
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    text_lower = raw_text.lower()
    
    # 1. Candidate Name
    candidate_name = extract_candidate_name_from_text(raw_text)

    # 2. Email & Phone
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    email = email_match.group(0) if email_match else None
    
    phone_match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', raw_text)
    phone = phone_match.group(0) if phone_match else None

    # 3. Technical Skills
    found_tech_skills = []
    for skill in TECHNICAL_SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_tech_skills.append(skill.title())

    # 4. Soft Skills
    found_soft_skills = []
    for skill in SOFT_SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_soft_skills.append(skill.title())

    # 5. Education
    edu_keywords = ["bachelor", "master", "phd", "b.e", "b.tech", "b.sc", "computer engineering", "university", "college", "degree"]
    edu_lines = []
    for line in lines:
        if any(ek in line.lower() for ek in edu_keywords):
            edu_lines.append(line)
    education = " | ".join(edu_lines[:3]) if edu_lines else "Bachelor in Computer Engineering / Related Field"

    # 6. Experience
    exp_keywords = ["experience", "intern", "developer", "engineer", "worked at", "responsibilities", "project", "developed"]
    exp_lines = []
    for line in lines:
        if any(ek in line.lower() for ek in exp_keywords):
            exp_lines.append(line)
    experience = " | ".join(exp_lines[:4]) if exp_lines else "Academic and project development experience."

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "technical_skills": list(set(found_tech_skills)),
        "soft_skills": list(set(found_soft_skills)),
        "raw_text": raw_text
    }
