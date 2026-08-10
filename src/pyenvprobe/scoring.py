from __future__ import annotations

from pyenvprobe.models import CheckResult, Severity, Status

# Point deductions based on Severity and Status
DEDUCTIONS = {
    (Status.FAIL, Severity.CRITICAL): 30,
    (Status.FAIL, Severity.HIGH): 15,
    (Status.FAIL, Severity.MEDIUM): 10,
    (Status.FAIL, Severity.LOW): 5,
    (Status.WARN, Severity.CRITICAL): 20,
    (Status.WARN, Severity.HIGH): 10,
    (Status.WARN, Severity.MEDIUM): 5,
    (Status.WARN, Severity.LOW): 2,
}


def calculate_health_score(results: list[CheckResult]) -> int:
    """Calculates a deterministic project health score from 0 to 100.

    Deductions are based on severity of warning/failure checks:
    - FAIL + CRITICAL: -30 points (e.g. secret files exposed, no python files)
    - FAIL + HIGH: -15 points (e.g. missing README, LICENSE, pyproject.toml)
    - FAIL + MEDIUM: -10 points (e.g. no tests directory)
    - WARN + MEDIUM: -5 points (e.g. unignored cache dirs, unpinned dependencies)
    - WARN + LOW: -2 points (e.g. missing optional configs like pytest or Ruff)
    - PASS, INFO, SKIP: -0 points
    """
    total_deductions = 0

    for result in results:
        # Check if the status has an associated deduction
        deduction = DEDUCTIONS.get((result.status, result.severity), 0)
        total_deductions += deduction

    score = 100 - total_deductions
    return max(0, min(100, score))
