#!/usr/bin/env python
"""
run.py
Root launcher for AI-Powered Intelligent Video Interview Assessment System.
"""

import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app

if __name__ == "__main__":
    print("=" * 72)
    print("  AI-POWERED INTELLIGENT VIDEO INTERVIEW ASSESSMENT SYSTEM")
    print("  Multimodal Deep Learning & Computer Vision Platform")
    print("=" * 72)
    print("  >> Server running at: http://localhost:5000")
    print("=" * 72)
    app.run(host="0.0.0.0", port=5000, debug=True)
