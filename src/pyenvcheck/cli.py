from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pyenvcheck.checks import run_all_checks
from pyenvcheck.models import Severity, Status
from pyenvcheck.output import format_cli_output, format_json_output
from pyenvcheck.scanner import scan_project
from pyenvcheck.scoring import calculate_health_score

__version__ = "0.1.0"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pyenvcheck",
        description="A lightweight checkup and health analysis tool for Python projects.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory to scan (default: current directory).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed messages and recommendations for all checks.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress all standard stdout messages.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in machine-readable JSON format.",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Enable CI mode. Returns exit code 1 if health score is below threshold or critical failures are found.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Minimum health score required to pass in CI mode (default: 80).",
    )
    parser.add_argument(
        "--category",
        action="append",
        help="Only run checks in the specified category (can be specified multiple times).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist.", file=sys.stderr)
        return 2

    if not target_path.is_dir():
        print(f"Error: Path '{target_path}' is not a directory.", file=sys.stderr)
        return 2

    # Parse categories filter
    categories_filter: list[str] | None = None
    if args.category:
        categories_filter = []
        for cat in args.category:
            # Handle comma-separated lists
            categories_filter.extend(c.strip().lower() for c in cat.split(","))

    # 1. Scan target directory
    context = scan_project(target_path)

    # 2. Run checks
    results = run_all_checks(context, categories=categories_filter)

    # 3. Calculate health score
    score = calculate_health_score(results)

    # 4. Handle JSON output
    if args.json:
        json_str = format_json_output(context, results, score)
        if not args.quiet:
            print(json_str)
    # 5. Handle standard output
    elif not args.quiet:
        cli_str = format_cli_output(context, results, score, verbose=args.verbose)
        print(cli_str)

    # 6. CI Mode exit logic
    if args.ci:
        # Check if score is below target threshold
        if score < args.threshold:
            if not args.quiet:
                print(
                    f"\nCI Failure: Health score {score} is below the threshold of {args.threshold}.",
                    file=sys.stderr,
                )
            return 1

        # Check if there are any CRITICAL failures
        has_critical = any(
            res.status == Status.FAIL and res.severity == Severity.CRITICAL
            for res in results
        )
        if has_critical:
            if not args.quiet:
                print(
                    "\nCI Failure: Critical diagnostic failures were detected.",
                    file=sys.stderr,
                )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
