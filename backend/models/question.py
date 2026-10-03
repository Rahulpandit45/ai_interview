import json
from datetime import datetime
from backend.services.database import db

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # technical, behavioral, communication, general
    target_role = db.Column(db.String(100), default="General")
    difficulty = db.Column(db.String(20), default="medium")
    question_text = db.Column(db.Text, nullable=False)
    expected_keywords = db.Column(db.Text, nullable=True) # JSON list
    benchmark_answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_keywords(self):
        try:
            return json.loads(self.expected_keywords) if self.expected_keywords else []
        except Exception:
            return []

    def set_keywords(self, keywords):
        self.expected_keywords = json.dumps(keywords)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "target_role": self.target_role,
            "difficulty": self.difficulty,
            "question_text": self.question_text,
            "expected_keywords": self.get_keywords(),
            "benchmark_answer": self.benchmark_answer
        }

def seed_default_questions():
    if Question.query.first() is not None:
        return

    import os
    import json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "datasets", "it_questions.json")
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            # Seed representative questions across categories
            for q in items[:50]:
                item = Question(
                    category=q.get("category", "General"),
                    target_role="Software Engineer",
                    difficulty=q.get("difficulty", "easy").lower(),
                    question_text=q["question"],
                    benchmark_answer=q.get("answer_2") or q.get("answer_1")
                )
                item.set_keywords([q.get("category", "").lower(), "fundamentals", "concept"])
                db.session.add(item)
            db.session.commit()
            print(f"[Seed] Added {min(50, len(items))} standard IT questions from dataset.")
            return
        except Exception as e:
            print(f"[Seed Warning] Error seeding from dataset: {e}")

    default_questions = [
        {
            "category": "Programming",
            "target_role": "General",
            "difficulty": "easy",
            "question_text": "What is Python?",
            "keywords": ["python", "programming", "language", "interpreted"],
            "benchmark_answer": "Python is an easy-to-read, high-level, dynamically typed programming language."
        },
        {
            "category": "Database & SQL",
            "target_role": "Software Engineer",
            "difficulty": "medium",
            "question_text": "What is a primary key?",
            "keywords": ["primary", "key", "unique", "database", "sql"],
            "benchmark_answer": "A primary key is a column or set of columns that uniquely identifies each row in a database table."
        }
    ]

    for q in default_questions:
        item = Question(
            category=q["category"],
            target_role=q["target_role"],
            difficulty=q["difficulty"],
            question_text=q["question_text"],
            benchmark_answer=q["benchmark_answer"]
        )
        item.set_keywords(q["keywords"])
        db.session.add(item)
    db.session.commit()
    print(f"[Seed] Added {len(default_questions)} default interview benchmark questions.")
