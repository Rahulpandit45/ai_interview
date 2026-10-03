#!/usr/bin/env python
"""
view_db.py - Convenient CLI script to inspect interview_db.sqlite records
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "interview_db.sqlite")

def inspect_database():
    if not os.path.exists(DB_PATH):
        print(f"[Error] Database file not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]

    print("=" * 80)
    print(f"  DATABASE CONTENTS: {DB_PATH}")
    print("=" * 80)

    for t in tables:
        cur.execute(f"SELECT * FROM {t};")
        rows = cur.fetchall()
        print(f"\n[*] TABLE: {t.upper()} ({len(rows)} records)")
        print("-" * 80)

        if not rows:
            print("  (Empty table)")
            continue

        cols = list(rows[0].keys())
        # Custom display columns for users table to highlight Candidate ID and Photo
        display_cols = cols
        if t.lower() == "users":
            priority = ["id", "admin_id", "candidate_id", "full_name", "email", "role", "institution", "profile_photo"]
            display_cols = [c for c in priority if c in cols] + [c for c in cols if c not in priority]
            display_cols = display_cols[:8]
        else:
            display_cols = cols[:6]

        # Print header
        header_str = " | ".join(display_cols)
        print(f"  {header_str}")
        print("  " + "-" * min(100, len(header_str) + 5))

        for row in rows[:10]:
            vals = [str(row[c])[:32] if row[c] is not None else "None" for c in display_cols]
            print("  " + " | ".join(vals))

        if len(rows) > 10:
            print(f"  ... and {len(rows) - 10} more rows")

    conn.close()
    print("\n" + "=" * 80)
    print("  You can also explore this interactively in your browser at:")
    print("  -> http://localhost:5000/db_viewer.html")
    print("=" * 80)

if __name__ == "__main__":
    inspect_database()
