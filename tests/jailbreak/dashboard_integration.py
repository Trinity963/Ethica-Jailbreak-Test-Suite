# ethica_trainer/tests/jailbreak/dashboard_integration.py
"""
Kernel Dashboard integration for the Jailbreak Test Suite.
Adds security testing status to the Ethica Kernel Dashboard.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field

from .runner import JailbreakTestRunner


@dataclass
class SecurityStatus:
    """Security test status for the dashboard."""
    status: str  # PASS, FAIL, WARNING, NEVER_RUN
    last_run: Optional[str] = None
    last_suite: Optional[str] = None
    refusals: int = 0
    total_turns: int = 0
    max_severity: str = "NONE"
    max_drift: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    report_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "last_run": self.last_run,
            "last_suite": self.last_suite,
            "refusals": self.refusals,
            "total_turns": self.total_turns,
            "max_severity": self.max_severity,
            "max_drift": self.max_drift,
            "errors": self.errors,
            "warnings": self.warnings,
            "report_path": self.report_path
        }


class SecurityDashboard:
    """
    Manages security test status for the Ethica Kernel Dashboard.
    Reads from test_runs directory and provides status summaries.
    """

    def __init__(self, test_runs_dir: Optional[Path] = None):
        self.test_runs_dir = test_runs_dir or Path(__file__).parent / "test_runs"
        self.test_runs_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_status(self, suite_name: Optional[str] = None) -> SecurityStatus:
        """Get the latest test status for a suite, or across all suites."""
        reports = self._find_reports(suite_name)

        if not reports:
            return SecurityStatus(
                status="NEVER_RUN",
                last_run=None,
                warnings=["No test runs found. Run the Jailbreak Test Suite to get started."]
            )

        # Get the most recent report
        latest_report = reports[-1]
        data = self._load_report(latest_report)

        if not data:
            return SecurityStatus(
                status="ERROR",
                warnings=["Could not parse latest test report."]
            )

        return SecurityStatus(
            status=data.get("status", "UNKNOWN"),
            last_run=data.get("timestamp"),
            last_suite=data.get("suite_name"),
            refusals=data.get("refusals", 0),
            total_turns=data.get("total_turns", 0),
            max_severity=data.get("max_severity", "NONE"),
            max_drift=data.get("max_drift_score", 0.0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            report_path=str(latest_report)
        )

    def get_all_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent test results for historical view."""
        reports = self._find_reports()
        results = []

        for report_path in reports[-limit:]:
            data = self._load_report(report_path)
            if data:
                results.append({
                    "suite": data.get("suite_name", "unknown"),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status", "UNKNOWN"),
                    "refusals": data.get("refusals", 0),
                    "total_turns": data.get("total_turns", 0),
                    "max_severity": data.get("max_severity", "NONE"),
                    "report_path": str(report_path)
                })

        return results

    def run_test_suite(self, suite_name: str = "crescendo", model_name: str = "trinity") -> SecurityStatus:
        """Run a test suite and return status."""
        runner = JailbreakTestRunner(
            model_name=model_name,
            test_dir=self.test_runs_dir,
            verbose=True
        )

        # Run the test
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(
            runner.run_test_suite(suite_name=suite_name)
        )

        # Return status
        return SecurityStatus(
            status=results.get("status", "UNKNOWN"),
            last_run=datetime.now().isoformat(),
            last_suite=suite_name,
            refusals=results.get("result", {}).get("refusals", 0),
            total_turns=results.get("result", {}).get("total_turns", 0),
            max_severity=results.get("result", {}).get("max_severity", "NONE"),
            max_drift=results.get("result", {}).get("max_drift_score", 0.0),
            report_path=results.get("report_paths", {}).get("html")
        )

    def _find_reports(self, suite_name: Optional[str] = None) -> List[Path]:
        """Find all report JSON files in test_runs."""
        if suite_name:
            pattern = self.test_runs_dir / f"*_{suite_name}_*/jailbreak_report_*.json"
        else:
            pattern = self.test_runs_dir / "*/jailbreak_report_*.json"

        reports = sorted(list(self.test_runs_dir.glob(str(pattern))), key=lambda p: p.stat().st_mtime)
        return reports

    def _load_report(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load a report JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None


# Dashboard panel for the Kernel Dashboard
def get_security_panel_data(test_runs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Gets security panel data for the Kernel Dashboard.
    Called by the dashboard module.
    """
    dashboard = SecurityDashboard(test_runs_dir)
    latest = dashboard.get_latest_status()

    # Status badge and color
    status_badges = {
        "PASS": {"icon": "🟢", "color": "#2e7d32", "label": "Passed"},
        "FAIL": {"icon": "🔴", "color": "#c62828", "label": "Failed"},
        "WARNING": {"icon": "🟡", "color": "#f57f17", "label": "Warning"},
        "NEVER_RUN": {"icon": "⚪", "color": "#757575", "label": "Not Run"},
        "ERROR": {"icon": "💥", "color": "#b71c1c", "label": "Error"}
    }
    badge = status_badges.get(latest.status, status_badges["ERROR"])

    return {
        "security": {
            "status": latest.status,
            "status_icon": badge["icon"],
            "status_color": badge["color"],
            "status_label": badge["label"],
            "last_run": latest.last_run,
            "last_suite": latest.last_suite,
            "refusals": latest.refusals,
            "total_turns": latest.total_turns,
            "max_severity": latest.max_severity,
            "max_drift": latest.max_drift,
            "warnings": latest.warnings,
            "errors": latest.errors,
            "report_path": latest.report_path
        },
        "history": dashboard.get_all_results(limit=5)
    }


# Command to run from the dashboard
def run_security_test_from_dashboard(suite_name: str = "crescendo", model_name: str = "trinity") -> dict:
    """
    Runs a security test and returns status for the dashboard.
    This is called when the user clicks "Run Security Test" in the UI.
    """
    dashboard = SecurityDashboard()
    result = dashboard.run_test_suite(suite_name, model_name)
    return result.to_dict()
