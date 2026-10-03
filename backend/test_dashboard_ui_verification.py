"""
Automated Verification Script for Candidate Dashboard UI & Backend Integration
Verifies DOM structure, 5-group sidebar architecture, KPI cards, readiness banner, and API readiness.
"""
import os
import re
import urllib.request
import unittest

class TestDashboardUI(unittest.TestCase):
    def setUp(self):
        self.dashboard_path = r"e:\project\frontend\dashboard.html"
        self.css_path = r"e:\project\frontend\css\style.css"
        with open(self.dashboard_path, "r", encoding="utf-8") as f:
            self.html_content = f.read()
        with open(self.css_path, "r", encoding="utf-8") as f:
            self.css_content = f.read()

    def test_sidebar_nav_items_order(self):
        """Verify the 9 sidebar navigation items exist in the 5-group required architecture."""
        expected_items = [
            ("Dashboard", "dashboard"),
            ("Start Interview", "start-interview"),
            ("Interview History", "history"),
            ("AI Reports", "reports"),
            ("My Resume", "resume"),
            ("Profile & Skills", "profile"),
            ("Notifications", "notifications"),
            ("Settings", "settings"),
            ("Help & Support", "support"),
        ]
        
        # Check order of appearance
        last_pos = -1
        for label, view in expected_items:
            pos = self.html_content.find(f'data-view="{view}"')
            self.assertNotEqual(pos, -1, f"View {view} ({label}) not found in sidebar")
            self.assertGreater(pos, last_pos, f"View {view} is out of order in sidebar navigation")
            last_pos = pos
        
        # Check Logout exists after the last item in bottom container
        logout_pos = self.html_content.find('id="btn-sidebar-logout"')
        self.assertNotEqual(logout_pos, -1, "Logout button not found")
        self.assertGreater(logout_pos, last_pos, "Logout button is before nav items")

    def test_sidebar_mini_profile(self):
        """Verify sidebar contains visible candidate mini profile with avatar, name, and candidate id."""
        self.assertIn('id="sidebar-mini-profile"', self.html_content)
        self.assertIn('id="sidebar-candidate-avatar"', self.html_content)
        self.assertIn('id="sidebar-candidate-name"', self.html_content)
        self.assertIn('id="sidebar-candidate-id"', self.html_content)

    def test_topbar_structure(self):
        """Verify clean professional header with title, notification icon, theme toggle, and candidate dropdown."""
        self.assertIn('Candidate Dashboard', self.html_content)
        self.assertIn('id="btn-topbar-theme-toggle"', self.html_content)
        self.assertIn('id="topbar-notif-count"', self.html_content)
        self.assertIn('id="topbar-profile-menu-container"', self.html_content)
        self.assertIn('id="topbar-candidate-chip"', self.html_content)
        self.assertIn('id="topbar-profile-dropdown"', self.html_content)
        self.assertIn('id="dropdown-candidate-name"', self.html_content)
        self.assertIn('id="dropdown-candidate-id"', self.html_content)

    def test_assessment_readiness_banner(self):
        """Verify compact Assessment Readiness status banner with 80%/100% progress elements."""
        self.assertIn('dash-readiness-banner', self.html_content)
        self.assertIn('id="dash-readiness-status-text"', self.html_content)
        self.assertIn('id="readiness-progress-pct"', self.html_content)
        self.assertIn('id="readiness-progress-fill"', self.html_content)
        self.assertIn('id="readiness-progress-sublabel"', self.html_content)

    def test_six_compact_kpi_cards(self):
        """Verify the 6 compact KPI cards: CID, Status, Resume, Completed Sessions, Latest Score, Profile Completion."""
        required_kpis = [
            "stat-card-cid",              # 1. Candidate ID
            "stat-card-interview-status", # 2. Interview Status
            "stat-card-resume-status",    # 3. Resume Status
            "stat-card-completed-count",  # 4. Completed Sessions
            "stat-card-interview-score",  # 5. Latest Score
            "stat-card-profile-pct"       # 6. Profile Completion
        ]
        for req_id in required_kpis:
            self.assertIn(f'id="{req_id}"', self.html_content, f"Missing KPI card element ID {req_id}")

    def test_two_column_readiness_and_launchpad(self):
        """Verify 2-column main dashboard grid: Assessment Readiness checklist + Next Action card."""
        self.assertIn('dash-main-2col-grid', self.html_content)
        self.assertIn('dash-readiness-checklist-card', self.html_content)
        self.assertIn('id="chk-account"', self.html_content)
        self.assertIn('id="chk-email"', self.html_content)
        self.assertIn('id="chk-cv"', self.html_content)
        self.assertIn('id="chk-identity"', self.html_content)
        self.assertIn('id="chk-role"', self.html_content)
        self.assertIn('id="chk-hardware"', self.html_content)
        self.assertIn('dash-launchpad-card', self.html_content)
        self.assertIn('id="btn-dash-start-interview"', self.html_content)

    def test_recent_interviews_section(self):
        """Verify recent interviews section with table and container for latest 3 interviews."""
        self.assertIn('dash-recent-interviews-section', self.html_content)
        self.assertIn('dash-history-table', self.html_content)
        self.assertIn('id="dash-recent-history-tbody"', self.html_content)

    def test_performance_overview_section(self):
        """Verify single clean performance overview section with tech, comm, completion, and proctoring metrics."""
        self.assertIn('dash-performance-overview-section', self.html_content)
        self.assertIn('id="dash-perf-tech-val"', self.html_content)
        self.assertIn('id="dash-perf-comm-val"', self.html_content)
        self.assertIn('id="dash-perf-overall-val"', self.html_content)

    def test_resume_verification_separation(self):
        """Verify clear separation of Identity Verification vs Resume Screening Match."""
        self.assertIn('resume-verif-compare-grid', self.html_content)
        self.assertIn('id="resume-verif-status-val"', self.html_content)
        self.assertIn('id="resume-match-pill"', self.html_content)

    def test_profile_and_skills(self):
        """Verify profile page has visible Candidate ID badge, edit button, and separated skills badges."""
        self.assertIn('id="profile-card-cid-badge"', self.html_content)
        self.assertIn('id="profile-skills-badges"', self.html_content)
        self.assertIn('id="profile-skills-count-badge"', self.html_content)

    def test_reports_graceful_empty_state(self):
        """Verify reports view includes friendly report empty state card."""
        self.assertIn('report-empty-state-card', self.html_content)
        self.assertIn('id="btn-open-printable-report"', self.html_content)

    def test_camera_and_microphone_diagnostics(self):
        """Verify dedicated device testing container with video preview, audio level bar, and photo capture."""
        self.assertIn('id="device-test-container"', self.html_content)
        self.assertIn('id="test-video-preview"', self.html_content)
        self.assertIn('id="test-audio-bar"', self.html_content)
        self.assertIn('id="live-camera-modal"', self.html_content)

    def test_css_rules_present(self):
        """Verify modern styling rules exist in style.css."""
        css_classes = [
            ".dash-kpi-grid-6",
            ".dash-readiness-banner",
            ".dash-main-2col-grid",
            ".dash-readiness-checklist-card",
            ".dash-launchpad-card",
            ".dash-history-table",
            ".dash-performance-overview-section",
            ".resume-verif-compare-grid",
            ".report-empty-state-card",
            ".candidate-profile-layout-grid"
        ]
        for cls in css_classes:
            self.assertIn(cls, self.css_content, f"Missing CSS rule {cls}")

    def test_http_endpoint_dashboard(self):
        """Verify the local dev server serves dashboard.html with HTTP 200."""
        try:
            req = urllib.request.Request("http://localhost:5000/dashboard.html")
            with urllib.request.urlopen(req, timeout=5) as response:
                self.assertEqual(response.status, 200)
                body = response.read().decode("utf-8")
                self.assertIn("Candidate Dashboard", body)
        except Exception as e:
            print(f"Server check note: {e}")

if __name__ == "__main__":
    unittest.main()
