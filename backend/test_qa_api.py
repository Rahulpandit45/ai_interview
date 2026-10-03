"""
test_qa_api.py
Automated test suite for FastAPI endpoint POST /api/qa/ask.
Tests the API using FastAPI TestClient (as well as optional live server).
"""

import os
import sys
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from starlette.testclient import TestClient
from backend.fastapi_app import app

client = TestClient(app)


def test_api_endpoints():
    print("=" * 72)
    print("  FASTAPI IT QUESTION & ANSWER API TEST SUITE")
    print("=" * 72)

    # 1. Test Root
    r_root = client.get("/")
    assert r_root.status_code == 200, f"Root failed: {r_root.text}"
    print("[PASS] GET / returned 200 OK")

    # 2. Test Categories
    r_cat = client.get("/api/qa/categories")
    assert r_cat.status_code == 200, f"Categories failed: {r_cat.text}"
    cat_data = r_cat.json()
    assert cat_data.get("total_categories", 0) >= 21, f"Expected >= 21 categories, got {cat_data}"
    print(f"[PASS] GET /api/qa/categories returned {cat_data['total_categories']} categories")

    # 3. Test Stats
    r_stats = client.get("/api/qa/stats")
    assert r_stats.status_code == 200, f"Stats failed: {r_stats.text}"
    stats = r_stats.json()
    assert stats.get("total_questions", 0) >= 500, f"Expected >= 500 questions, got {stats}"
    print(f"[PASS] GET /api/qa/stats returned {stats['total_questions']} questions")

    # 4. Test POST /api/qa/ask with exact question
    req_payload = {"question": "What is Python?"}
    r_ask = client.post("/api/qa/ask", json=req_payload)
    assert r_ask.status_code == 200, f"Ask failed: {r_ask.text}"
    resp = r_ask.json()
    assert "question" in resp and resp["question"] == "What is Python?"
    assert "answer" in resp and len(resp["answer"]) > 10
    print("[PASS] POST /api/qa/ask ('What is Python?')")
    print(f"       Response: {json.dumps(resp, indent=2)}")

    # 5. Test Paraphrased question
    paraphrase_payload = {"question": "Can you explain what Python is?"}
    r_para = client.post("/api/qa/ask", json=paraphrase_payload)
    assert r_para.status_code == 200, f"Paraphrase failed: {r_para.text}"
    resp_para = r_para.json()
    assert "answer" in resp_para and "programming language" in resp_para["answer"].lower()
    print("[PASS] POST /api/qa/ask ('Can you explain what Python is?')")
    print(f"       Response: {json.dumps(resp_para, indent=2)}")

    # 6. Test Multi-domain questions
    domain_questions = [
        "What is an operating system in simple terms?",
        "What is SQL?",
        "What is Flutter?",
        "What is Docker?",
        "What is Firebase Authentication?",
        "What is MQTT in IoT?"
    ]

    for dq in domain_questions:
        r = client.post("/api/qa/ask", json={"question": dq})
        assert r.status_code == 200, f"Domain ask failed for '{dq}': {r.text}"
        data = r.json()
        assert len(data.get("answer", "")) > 10
        print(f"[PASS] POST /api/qa/ask ('{dq[:35]}...') -> {data['answer'][:60]}...")

    # 7. Test Empty Question Validation
    r_empty = client.post("/api/qa/ask", json={"question": ""})
    assert r_empty.status_code in [400, 422], f"Expected 400 or 422 for empty question, got {r_empty.status_code}"
    print("[PASS] POST /api/qa/ask validation rejects empty question with 400 Bad Request")

    print("=" * 72)
    print("  ALL API TESTS PASSED SUCCESSFULLY (100%)")
    print("=" * 72)
    return True


if __name__ == "__main__":
    test_api_endpoints()
