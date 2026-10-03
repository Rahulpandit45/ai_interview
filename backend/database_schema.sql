-- AI-Powered Intelligent Video Interview Assessment System
-- MySQL Database Schema Definition

CREATE DATABASE IF NOT EXISTS interview_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE interview_db;

-- 1. Users Table (Candidates & Admins)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_id VARCHAR(50) UNIQUE, -- Unique permanent Candidate ID (e.g. CID-2026-9E4B2A)
    admin_id VARCHAR(50) UNIQUE, -- Official institutional Admin ID (e.g. ADM-2026-001)
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'candidate', -- 'candidate' or 'admin' / 'recruiter'
    institution VARCHAR(120) DEFAULT 'Mid-West University', -- Issuing company or university
    phone VARCHAR(30),
    target_role VARCHAR(100) DEFAULT 'Software Engineer',
    profile_photo VARCHAR(255), -- Relative path to uploaded candidate profile photo
    email_verified BOOLEAN DEFAULT 0, -- Set to 1 when verified via OTP
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    raw_text LONGTEXT,
    candidate_name VARCHAR(120),
    education TEXT,
    experience TEXT,
    technical_skills JSON,
    soft_skills JSON,
    screening_score FLOAT DEFAULT 0.0,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'technical', 'behavioral', 'communication', 'general'
    target_role VARCHAR(100) DEFAULT 'General',
    difficulty VARCHAR(20) DEFAULT 'medium',
    question_text TEXT NOT NULL,
    expected_keywords JSON,
    benchmark_answer TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Interviews Table
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_role VARCHAR(100) NOT NULL,
    status VARCHAR(30) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'cancelled'
    overall_score FLOAT DEFAULT 0.0,
    communication_score FLOAT DEFAULT 0.0,
    technical_score FLOAT DEFAULT 0.0,
    confidence_score FLOAT DEFAULT 0.0,
    eye_contact_score FLOAT DEFAULT 0.0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Interview Responses Table (Per Question)
CREATE TABLE IF NOT EXISTS interview_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_id INT,
    question_text TEXT NOT NULL,
    video_path VARCHAR(500),
    audio_path VARCHAR(500),
    transcript TEXT,
    relevance_score FLOAT DEFAULT 0.0,
    technical_score FLOAT DEFAULT 0.0,
    sentiment VARCHAR(30) DEFAULT 'Neutral',
    duration_seconds FLOAT DEFAULT 0.0,
    eye_contact_pct FLOAT DEFAULT 0.0,
    head_stability_pct FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

-- 6. Assessment Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    candidate_name VARCHAR(120) NOT NULL,
    target_role VARCHAR(100) NOT NULL,
    overall_score FLOAT NOT NULL,
    communication_score FLOAT NOT NULL,
    technical_score FLOAT NOT NULL,
    confidence_score FLOAT NOT NULL,
    eye_contact_pct FLOAT NOT NULL,
    head_movement_score FLOAT NOT NULL,
    facial_engagement_score FLOAT NOT NULL,
    speech_fluency_wpm FLOAT NOT NULL,
    resume_score FLOAT DEFAULT 0.0,
    strengths JSON,
    weaknesses JSON,
    feedback TEXT,
    detailed_metrics JSON,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Email OTP Verification Table (Candidate Registration)
CREATE TABLE IF NOT EXISTS email_otps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    attempts INT DEFAULT 0,
    is_used BOOLEAN DEFAULT 0,
    purpose VARCHAR(50) DEFAULT 'candidate_registration',
    last_sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_email_otps_email (email),
    INDEX ix_email_otps_expires (expires_at)
);

