import re
import pandas as pd
import logging
from src.rule_loader import Rule
from src.db_connector import get_table

logger = logging.getLogger(__name__)


# ── INDIVIDUAL RULE HANDLERS ──────────────────────────────────────────────────

def check_null(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    col = rule.column
    mask = df[col].isnull()
    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = None
    return bad_rows


def check_range(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    col = rule.column
    min_val = rule.params.get("min")
    max_val = rule.params.get("max")

    mask = pd.Series([False] * len(df), index=df.index)

    if min_val is not None:
        mask |= df[col].lt(min_val)
    if max_val is not None:
        mask |= df[col].gt(max_val)

    # Skip nulls — null_check handles those separately
    mask &= df[col].notnull()

    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = df.loc[mask, col]
    return bad_rows


def check_regex(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    col = rule.column
    pattern = rule.params.get("pattern", "")
    compiled = re.compile(pattern)

    def fails_pattern(val):
        if pd.isnull(val):
            return False  # null_check handles nulls
        return not bool(compiled.match(str(val)))

    mask = df[col].apply(fails_pattern)
    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = df.loc[mask, col]
    return bad_rows


def check_allowed_values(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    col = rule.column
    allowed = rule.params.get("values", [])

    mask = df[col].notnull() & ~df[col].isin(allowed)
    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = df.loc[mask, col]
    return bad_rows


def check_uniqueness(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    col = rule.column
    mask = df.duplicated(subset=[col], keep=False) & df[col].notnull()
    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = df.loc[mask, col]
    return bad_rows


def check_referential(
    df: pd.DataFrame,
    rule: Rule,
    config_path: str = "config/db_config.yaml"
) -> pd.DataFrame:
    col = rule.column
    ref_table = rule.params.get("ref_table")
    ref_col = rule.params.get("ref_column")

    ref_df = get_table(ref_table, config_path)
    valid_values = set(ref_df[ref_col].dropna().unique())

    mask = df[col].notnull() & ~df[col].isin(valid_values)
    bad_rows = df[mask].copy()
    bad_rows["violated_value"] = df.loc[mask, col]
    return bad_rows


# ── RULE DISPATCHER ───────────────────────────────────────────────────────────

RULE_HANDLERS = {
    "null_check":           check_null,
    "range_check":          check_range,
    "regex_check":          check_regex,
    "allowed_values_check": check_allowed_values,
    "uniqueness_check":     check_uniqueness,
    "referential_check":    check_referential,
}


# ── MAIN VALIDATOR ────────────────────────────────────────────────────────────

def run_validation(
    rules: list[Rule],
    config_path: str = "config/db_config.yaml"
) -> pd.DataFrame:
    
    all_violations = []

    # Group rules by table to avoid fetching same table multiple times
    tables = set(r.table for r in rules)

    for table in tables:
        logger.info(f"Validating table: {table}")
        df = get_table(table, config_path)
        table_rules = [r for r in rules if r.table == table]

        for rule in table_rules:
            handler = RULE_HANDLERS.get(rule.rule_type)

            if not handler:
                logger.warning(f"Unknown rule type: {rule.rule_type} — skipping {rule.rule_id}")
                continue

            try:
                if rule.rule_type == "referential_check":
                    bad_rows = handler(df, rule, config_path)
                else:
                    bad_rows = handler(df, rule)

                if bad_rows.empty:
                    logger.info(f"  ✓ {rule.rule_id} passed — no violations")
                    continue

                # Build violations records
                for _, row in bad_rows.iterrows():
                    all_violations.append({
                        "rule_id":       rule.rule_id,
                        "table":         rule.table,
                        "column":        rule.column,
                        "rule_type":     rule.rule_type,
                        "severity":      rule.severity,
                        "description":   rule.description,
                        "row_id":        row.get("emp_id", "N/A"),
                        "violated_value": row.get("violated_value", "NULL"),
                    })

                logger.info(f"  ✗ {rule.rule_id} — {len(bad_rows)} violation(s) found")

            except Exception as e:
                logger.error(f"Error running {rule.rule_id}: {e}")

    if not all_violations:
        logger.info("All rules passed. No violations found.")
        return pd.DataFrame()

    violations_df = pd.DataFrame(all_violations)

    # Sort by severity priority
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    violations_df["_sort"] = violations_df["severity"].map(severity_order)
    violations_df = violations_df.sort_values("_sort").drop(columns=["_sort"])
    violations_df = violations_df.reset_index(drop=True)

    return violations_df