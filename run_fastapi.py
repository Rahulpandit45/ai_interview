#!/usr/bin/env python
"""
run_fastapi.py
Launcher for FastAPI IT Question & Answer Backend.
Runs on http://localhost:8000 (Swagger docs available at http://localhost:8000/docs).
"""

import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print("=" * 72)
    print("  AI INTERVIEW SYSTEM - FASTAPI IT QUESTION & ANSWER SERVICE")
    print("  FastAPI + Uvicorn Async Serving")
    print("=" * 72)
    print("  >> Server running at:     http://localhost:8000")
    print("  >> Interactive API Docs:  http://localhost:8000/docs")
    print("  >> Endpoint:              POST http://localhost:8000/api/qa/ask")
    print("=" * 72)
    uvicorn.run("backend.fastapi_app:app", host="0.0.0.0", port=8000, reload=False)
