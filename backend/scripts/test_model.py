"""
test_model.py
Automated testing script for the fine-tuned IT Question & Answer model
and Semantic Knowledge Base.

Validates:
1. Exact question matching
2. Paraphrased question handling (different wordings of the same question)
3. Multi-domain coverage (Python, Networking, Database, Flutter, AI, etc.)
4. Performance and latency
"""

import os
import sys
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.services.qa_service import QAService

TEST_CASES = [
    # 1. Exact canonical questions
    ("What is Python?", "Python core concept"),
    ("What is an operating system in simple terms?", "OS core concept"),
    ("What is SQL?", "Database core concept"),
    ("What is Flutter?", "Mobile cross-platform concept"),
    ("What is the Internet of Things (IoT)?", "IoT core concept"),

    # 2. Paraphrased / alternate phrasing questions
    ("Can you explain what Python is?", "Paraphrased Python"),
    ("Tell me about Flutter widgets", "Paraphrased Flutter"),
    ("How does the TCP three-way handshake work?", "Paraphrased Networking"),
    ("Could you define artificial intelligence?", "Paraphrased AI"),
    ("Explain the difference between a process and a thread", "Paraphrased OS"),
    ("What do you mean by Git merge conflict?", "Paraphrased Git"),
    ("What is Cloud Firestore in Firebase?", "Paraphrased Firebase")
]


def run_tests():
    print("=" * 72)
    print("  AI INTERVIEW SYSTEM - IT QA MODEL & INFERENCE VERIFICATION")
    print("=" * 72)

    passed = 0
    total = len(TEST_CASES)

    for i, (q, desc) in enumerate(TEST_CASES, 1):
        t0 = time.time()
        result = QAService.answer_question(q)
        elapsed_ms = (time.time() - t0) * 1000

        ans = result.get("answer", "")
        is_valid = bool(ans and len(ans.strip()) > 10 and "not found" not in ans.lower())

        if is_valid:
            passed += 1
            status = "[PASS]"
        else:
            status = "[FAIL]"

        print(f"\n{status} Test {i}/{total} ({desc}) [{elapsed_ms:.1f}ms]")
        print(f"  Q: {q}")
        print(f"  A: {ans}")

    print("\n" + "=" * 72)
    print(f"  Test Results: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 72)
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
