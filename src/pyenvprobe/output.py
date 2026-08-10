from __future__ import annotations

import json
import os
import sys

from pyenvprobe.models import CheckResult, ProjectContext, Status

# ANSI Escape Codes for Colors
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_BLUE = "\033[34m"
COLOR_GREY = "\033[90m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

STATUS_ICONS = {
    Status.PASS: "✓",
    Status.WARN: "⚠",
    Status.FAIL: "✗",
    Status.SKIP: "-",
    Status.INFO: "ℹ",
}

STATUS_COLORS = {
    Status.PASS: COLOR_GREEN,
    Status.WARN: COLOR_YELLOW,
    Status.FAIL: COLOR_RED,
    Status.SKIP: COLOR_GREY,
    Status.INFO: COLOR_BLUE,
}

CATEGORY_NAMES = {
    "python": "Python",
    "structure": "Structure",
    "git": "Git",
    "documentation": "Documentation",
    "testing": "Testing",
    "tooling": "Tooling",
    "dependencies": "Dependencies",
    "hygiene": "Hygiene",
    "security": "Security",
}


def support_color() -> bool:
    """Checks if the current terminal output supports ANSI colors."""
    # Check if stdout is a TTY and check environment variables (like NO_COLOR)
    if "NO_COLOR" in os.environ:
        return False
    # Windows support for colors via virtual terminal processing is usually enabled in modern systems
    return sys.stdout.isatty()


def get_ui_symbols() -> tuple[dict[Status, str], str]:
    """Gets status icons and separators based on terminal encoding support."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        # Test encoding standard diagnostic characters
        "✓".encode(encoding)
        "─".encode(encoding)
        return STATUS_ICONS, "────────────────────────────────"
    except (UnicodeEncodeError, AttributeError, LookupError):
        # Fallback symbols for cp1252 or other non-Unicode encodings
        ascii_icons = {
            Status.PASS: "+",
            Status.WARN: "!",
            Status.FAIL: "x",
            Status.SKIP: "-",
            Status.INFO: "i",
        }
        return ascii_icons, "--------------------------------"


def format_cli_output(
    context: ProjectContext,
    results: list[CheckResult],
    score: int,
    verbose: bool = False,
) -> str:
    """Generates a beautiful human-readable string representation of check results."""
    use_color = support_color()
    icons, separator = get_ui_symbols()

    def color(text: str, color_code: str) -> str:
        return f"{color_code}{text}{COLOR_RESET}" if use_color else text

    lines = []
    lines.append(color("pyenvprobe Checkup", COLOR_BOLD))
    lines.append(separator)

    # Group results by category
    results_by_category: dict[str, list[CheckResult]] = {}
    for res in results:
        results_by_category.setdefault(res.category, []).append(res)

    # Order categories
    categories_order = [
        "python",
        "structure",
        "testing",
        "tooling",
        "git",
        "documentation",
        "dependencies",
        "hygiene",
        "security",
    ]
    # Add any extra categories that might be dynamically registered
    for cat in results_by_category:
        if cat not in categories_order:
            categories_order.append(cat)

    for cat in categories_order:
        cat_results = results_by_category.get(cat)
        if not cat_results:
            continue

        cat_title = CATEGORY_NAMES.get(cat, cat.capitalize())
        lines.append("")
        lines.append(color(cat_title, COLOR_BOLD))

        for res in cat_results:
            icon = icons.get(res.status, "?")
            c_code = STATUS_COLORS.get(res.status, COLOR_RESET)
            status_symbol = color(icon, c_code)

            lines.append(f"  {status_symbol} {res.title}")

            # Verbose info or failures details
            if verbose or res.status in (Status.FAIL, Status.WARN):
                lines.append(f"    {color('Message:', COLOR_GREY)} {res.message}")
                if res.recommendation:
                    lines.append(
                        f"    {color('Fix:', COLOR_GREY)} {res.recommendation}"
                    )

    # Print scanner errors
    if context.errors:
        lines.append("")
        lines.append(color("Scanner Errors / Warnings", COLOR_RED + COLOR_BOLD))
        for err in context.errors:
            lines.append(f"  ! {err}")

    # Health Score line
    lines.append("")
    lines.append(separator)

    score_color = COLOR_GREEN
    if score < 50:
        score_color = COLOR_RED
    elif score < 80:
        score_color = COLOR_YELLOW

    score_str = color(f"{score}/100", score_color + COLOR_BOLD)
    lines.append(f"Project health: {score_str}")

    return "\n".join(lines)


def format_json_output(
    context: ProjectContext, results: list[CheckResult], score: int
) -> str:
    """Formats the results conforming to the JSON schema defined in docs/JSON_SCHEMA.md."""
    summary = {
        "total": len(results),
        "pass": 0,
        "warn": 0,
        "fail": 0,
        "skip": 0,
        "info": 0,
    }

    serialized_results = []
    for res in results:
        status_lower = res.status.value.lower()
        if status_lower in summary:
            summary[status_lower] += 1
        serialized_results.append(res.to_dict())

    # Build root output dictionary
    output_dict = {
        "project_path": str(context.root_path).replace("\\", "/"),
        "score": score,
        "summary": summary,
        "results": serialized_results,
    }

    if context.errors:
        output_dict["errors"] = context.errors

    return json.dumps(output_dict, indent=2)
