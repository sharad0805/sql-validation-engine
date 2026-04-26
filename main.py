import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import logging
import os
import sys
from datetime import datetime

from src.rule_loader import load_rules, get_rules_for_table
from src.validator import run_validation
from src.report_generator import generate_report


# ── LOGGING SETUP ─────────────────────────────────────────────────────────────

def setup_logging(log_dir: str = "logs"):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = os.path.join(log_dir, f"run_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ]
    )
    return log_file


# ── CLI DEFINITION ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="SQL Data Validation & Reporting Engine",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--rules-config",
        default="config/rules.yaml",
        help="Path to rules YAML file (default: config/rules.yaml)"
    )
    parser.add_argument(
        "--db-config",
        default="config/db_config.yaml",
        help="Path to DB config YAML file (default: config/db_config.yaml)"
    )
    parser.add_argument(
        "--table",
        default=None,
        help="Validate a specific table only (default: all tables in rules)"
    )
    parser.add_argument(
        "--output-format",
        choices=["excel", "none"],
        default="excel",
        help="Output format: excel | none (default: excel)"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to save reports (default: reports/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation but do not generate report"
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        default=None,
        help="Show only violations at or above this severity level"
    )

    return parser


# ── SEVERITY FILTER ───────────────────────────────────────────────────────────

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

def filter_by_severity(violations_df, min_severity: str):
    if min_severity is None or violations_df.empty:
        return violations_df
    min_rank = SEVERITY_RANK[min_severity]
    return violations_df[
        violations_df["severity"].map(SEVERITY_RANK) <= min_rank
    ]


# ── PRINT SUMMARY TO CONSOLE ──────────────────────────────────────────────────

def print_summary(violations_df, rules):
    logger = logging.getLogger(__name__)

    logger.info("=" * 55)
    logger.info("  VALIDATION SUMMARY")
    logger.info("=" * 55)
    logger.info(f"  Total rules run   : {len(rules)}")
    logger.info(f"  Total violations  : {len(violations_df)}")

    if not violations_df.empty:
        for sev in ["critical", "high", "medium", "low"]:
            count = len(violations_df[violations_df["severity"] == sev])
            if count:
                logger.info(f"  {sev.capitalize():<10}        : {count}")

    logger.info("=" * 55)

    if not violations_df.empty:
        logger.info("\n  TOP VIOLATIONS:\n")
        for _, row in violations_df.head(10).iterrows():
            logger.info(
                f"  [{row['severity'].upper():<8}] "
                f"{row['rule_id']} | "
                f"{row['table']}.{row['column']} | "
                f"Row {row['row_id']} | "
                f"Value: {row['violated_value']}"
            )


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = build_parser()
    args   = parser.parse_args()

    log_file = setup_logging()
    logger   = logging.getLogger(__name__)

    logger.info("SQL Validation Engine started")
    logger.info(f"Log file: {log_file}")

    # Load rules
    if args.table:
        rules = get_rules_for_table(args.table, args.rules_config)
        if not rules:
            logger.error(f"No rules found for table: '{args.table}'")
            sys.exit(1)
        logger.info(f"Loaded {len(rules)} rules for table: {args.table}")
    else:
        rules = load_rules(args.rules_config)
        logger.info(f"Loaded {len(rules)} rules across all tables")

    # Run validation
    logger.info("Starting validation...\n")
    violations_df = run_validation(rules, config_path=args.db_config)

    # Apply severity filter
    if args.severity:
        violations_df = filter_by_severity(violations_df, args.severity)
        logger.info(f"Filtered to severity: {args.severity} and above")

    # Print summary
    print_summary(violations_df, rules)

    # Generate report
    if args.dry_run:
        logger.info("\nDry run mode — report not saved.")
    elif args.output_format == "excel":
        path = generate_report(
            violations_df,
            total_rules=len(rules),
            output_dir=args.output_dir
        )
        logger.info(f"\nReport saved -> {path}")

    # Exit code — useful for CI/CD pipelines
    if not violations_df.empty:
        critical_count = len(violations_df[violations_df["severity"] == "critical"])
        if critical_count > 0:
            logger.info(f"\nExiting with code 1 — {critical_count} critical violation(s) found")
            sys.exit(1)

    logger.info("\nDone.")


if __name__ == "__main__":
    main()