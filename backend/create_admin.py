#!/usr/bin/env python
"""
create_admin.py
Institutional CLI utility for company or university IT administrators
to provision official administrator accounts.

Usage:
  python backend/create_admin.py --name "Dr. Hari Prasad" --email "hari@mwu.edu.np" --password "SecureAdmin123" --institution "Mid-West University"
  python backend/create_admin.py (interactive prompt)
"""

import sys
import os
import argparse

# Ensure root workspace is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.services.database import db
from backend.models.user import User

def provision_admin_cli(name, email, password, institution="Mid-West University", target_role="Recruitment Lead", custom_admin_id=None, phone=""):
    app = create_app()
    with app.app_context():
        # Check existing email
        clean_email = email.strip().lower()
        if User.query.filter_by(email=clean_email).first():
            print(f"[ERROR] An account with email '{clean_email}' already exists.")
            return False

        # Generate or check Admin ID
        if custom_admin_id:
            clean_admin_id = custom_admin_id.strip().upper()
            if User.query.filter_by(admin_id=clean_admin_id).first():
                print(f"[ERROR] Admin ID '{clean_admin_id}' is already assigned.")
                return False
            admin_id = clean_admin_id
        else:
            admin_id = User.generate_admin_id()

        admin = User(
            admin_id=admin_id,
            full_name=name.strip(),
            email=clean_email,
            role="admin",
            institution=institution.strip(),
            target_role=target_role.strip(),
            phone=phone.strip() if phone else None
        )
        admin.set_password(password.strip())
        db.session.add(admin)
        db.session.commit()

        print("=" * 72)
        print("  OFFICIAL ADMINISTRATOR ACCOUNT PROVISIONED")
        print("=" * 72)
        print(f"  Official Admin ID : {admin.admin_id}")
        print(f"  Full Name         : {admin.full_name}")
        print(f"  Official Email    : {admin.email}")
        print(f"  Institution       : {admin.institution}")
        print(f"  Administrative Role: {admin.target_role}")
        print("=" * 72)
        print("  LOGIN INSTRUCTIONS:")
        print(f"  Navigate to the Administrator Portal at http://localhost:5000/login.html?portal=admin")
        print(f"  Sign in using:")
        print(f"    - Official Admin ID: {admin.admin_id}")
        print(f"    - Official Password: [AS CONFIGURED]")
        print("=" * 72)
        return True

def main():
    parser = argparse.ArgumentParser(description="Provision official Administrator account for University / Company")
    parser.add_argument("--name", help="Administrator Full Name")
    parser.add_argument("--email", help="Official Email Address")
    parser.add_argument("--password", help="Administrator Password (min 6 chars)")
    parser.add_argument("--institution", default="Mid-West University", help="Company or University Name")
    parser.add_argument("--role-title", default="Recruitment Lead", help="Administrative Title (e.g. Department Chair)")
    parser.add_argument("--admin-id", default=None, help="Custom Admin ID (default: auto-generated ADM-YYYY-XXX)")
    parser.add_argument("--phone", default="", help="Contact Phone Number")

    args = parser.parse_args()

    name = args.name
    email = args.email
    password = args.password
    institution = args.institution
    role_title = args.role_title
    admin_id = args.admin_id
    phone = args.phone

    if not name or not email or not password:
        print("\n--- Institutional Administrator Account Provisioning ---")
        name = input("Enter Full Name: ").strip()
        email = input("Enter Official Email: ").strip()
        import getpass
        password = getpass.getpass("Enter Password (min 6 chars): ").strip()
        inst_input = input(f"Enter Institution/Company [{institution}]: ").strip()
        if inst_input:
            institution = inst_input
        title_input = input(f"Enter Role Title [{role_title}]: ").strip()
        if title_input:
            role_title = title_input

    if not name or not email or not password:
        print("[ERROR] Full Name, Email, and Password are required.")
        sys.exit(1)

    if len(password) < 6:
        print("[ERROR] Password must be at least 6 characters.")
        sys.exit(1)

    success = provision_admin_cli(
        name=name,
        email=email,
        password=password,
        institution=institution,
        target_role=role_title,
        custom_admin_id=admin_id,
        phone=phone
    )

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
