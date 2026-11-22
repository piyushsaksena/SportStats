"""Command Line Interface for SportStats Ingestion Pipeline.

Supports batch CSV importing, dry-run validation, audit logs, and quality inspection.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from sportstats.db.session import SessionLocal
from sportstats.pipeline.importer import CSVImporter
from sportstats.pipeline.verification import VerificationWorkflow


def create_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser for sportstats pipeline commands."""
    parser = argparse.ArgumentParser(
        prog="sportstats-pipeline",
        description="SportStats Data Ingestion and Quality CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import a CSV dataset")
    import_parser.add_argument(
        "--type",
        required=True,
        choices=[
            "tournament_editions",
            "matches",
            "performance_stats",
            "rankings",
            "olympic_results",
        ],
        help="Type of CSV dataset being imported",
    )
    import_parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="Path to CSV data file",
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report errors without writing to the database",
    )

    # Import-all command
    import_all_parser = subparsers.add_parser("import-all", help="Import all CSVs from a directory")
    import_all_parser.add_argument(
        "--dir",
        required=True,
        type=Path,
        help="Directory containing tournament_editions.csv, matches.csv, etc.",
    )
    import_all_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report errors without writing to the database",
    )

    # List runs command
    subparsers.add_parser("list-runs", help="List previous ingestion runs and audit statuses")

    # Inspect run command
    inspect_parser = subparsers.add_parser(
        "inspect-run", help="Inspect itemized data quality issues for a run"
    )
    inspect_parser.add_argument(
        "--run-id",
        required=True,
        help="UUID of the ingestion run to inspect",
    )

    # Verify source command
    verify_parser = subparsers.add_parser(
        "verify-source", help="Approve an unverified or secondary source"
    )
    verify_parser.add_argument(
        "--source-id",
        required=True,
        help="UUID of the source to verify",
    )
    verify_parser.add_argument(
        "--reviewer",
        default="admin",
        help="Name of the reviewing administrator",
    )

    return parser


def main(args: Optional[list] = None) -> int:
    """Main CLI execution handler."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    db = SessionLocal()
    try:
        importer = CSVImporter(db)
        workflow = VerificationWorkflow(db)

        if parsed_args.command == "import":
            result = importer.import_csv(
                file_path=parsed_args.file,
                dataset_type=parsed_args.type,
                dry_run=parsed_args.dry_run,
            )
            print("=" * 60)
            print(f"Ingestion Result [{result.status.upper()}]:")
            print(f"  Run ID:        {result.run_id}")
            print(f"  Dry-Run Mode:  {result.dry_run}")
            print(f"  Rows In:       {result.rows_in}")
            print(f"  Rows Loaded:   {result.rows_loaded}")
            print(f"  Rows Rejected: {result.rows_rejected}")
            if result.issues:
                print("\nItemized Quality Issues:")
                for iss in result.issues:
                    print(
                        f"  - [{iss['severity'].upper()}] {iss['rule_code']} ({iss['row_ref']}): {iss['message']}"
                    )
            print("=" * 60)
            return 0 if result.rows_rejected == 0 else 1

        elif parsed_args.command == "import-all":
            target_dir = Path(parsed_args.dir)
            dataset_order = [
                ("tournament_editions.csv", "tournament_editions"),
                ("matches.csv", "matches"),
                ("performance_stats.csv", "performance_stats"),
                ("rankings.csv", "rankings"),
                ("olympic_results.csv", "olympic_results"),
            ]
            total_in = 0
            total_loaded = 0
            total_rejected = 0

            for filename, dtype in dataset_order:
                file_path = target_dir / filename
                if file_path.exists():
                    print(f"\nProcessing {filename} as {dtype}...")
                    res = importer.import_csv(file_path, dtype, dry_run=parsed_args.dry_run)
                    total_in += res.rows_in
                    total_loaded += res.rows_loaded
                    total_rejected += res.rows_rejected
                    print(
                        f"  Loaded: {res.rows_loaded}, Rejected: {res.rows_rejected}, Status: {res.status}"
                    )
                else:
                    print(f"Skipping {filename} (not found in directory)")

            print("\n" + "=" * 60)
            print(
                f"Batch Import Summary: In={total_in}, Loaded={total_loaded}, Rejected={total_rejected}"
            )
            print("=" * 60)
            return 0 if total_rejected == 0 else 1

        elif parsed_args.command == "list-runs":
            runs = workflow.get_pending_runs()
            print(f"Found {len(runs)} pending / flagged ingestion runs:")
            for r in runs:
                print(
                    f"  - Run {r.id}: Status={r.status}, Started={r.started_at}, In={r.rows_in}, Loaded={r.rows_loaded}, Rejected={r.rows_rejected}"
                )
            return 0

        elif parsed_args.command == "inspect-run":
            issues = workflow.get_run_issues(parsed_args.run_id)
            print(f"Run {parsed_args.run_id} has {len(issues)} recorded quality issues:")
            for iss in issues:
                print(
                    f"  [{iss.severity.upper()}] {iss.rule_code} at {iss.table_name} ({iss.row_ref}): {iss.message}"
                )
            return 0

        elif parsed_args.command == "verify-source":
            ok = workflow.approve_source(parsed_args.source_id, parsed_args.reviewer)
            if ok:
                print(
                    f"Source {parsed_args.source_id} successfully verified by {parsed_args.reviewer}."
                )
                return 0
            else:
                print(f"Source {parsed_args.source_id} not found.")
                return 1

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
