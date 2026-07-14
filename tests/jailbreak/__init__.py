# ethica_trainer/tests/jailbreak/__init__.py
"""
Jailbreak Test Suite for Ethica Sovereign Models.
Multi-turn attack testing, metrics, and reporting.
"""

from .runner import JailbreakTestRunner
from .metrics import JailbreakMetrics, TestResult, Severity, TestStatus
from .attack_suite import ATTACK_SUITES

__version__ = "1.0.0"
__all__ = [
    "JailbreakTestRunner",
    "JailbreakMetrics",
    "TestResult",
    "Severity",
    "TestStatus",
    "ATTACK_SUITES"
]
