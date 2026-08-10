from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Status(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"
    INFO = "INFO"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class CheckResult:
    id: str
    category: str
    title: str
    status: Status
    severity: Severity
    message: str
    recommendation: str
    metadata: dict[str, Any] = field(default_factory=dict)
    fixable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "status": self.status.value,
            "severity": self.severity.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
            "fixable": self.fixable,
        }


@dataclass
class ProjectContext:
    root_path: Path
    files: set[str] = field(default_factory=set)
    dirs: set[str] = field(default_factory=set)
    pyproject: dict[str, Any] = field(default_factory=dict)
    requirements_files: list[str] = field(default_factory=list)
    git_info: dict[str, Any] = field(default_factory=dict)
    large_files: list[tuple[str, int]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
