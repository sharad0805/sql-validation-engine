# from src.db_connector import get_table

# df = get_table("employees")
# print(df)
# print(f"\nShape: {df.shape}")
# print(f"\nColumns: {list(df.columns)}")


# from src.rule_loader import load_rules, get_rules_for_table

# Load all rules
# all_rules = load_rules()
# print(f"Total rules loaded: {len(all_rules)}\n")

# for rule in all_rules:
#     print(rule)

# # Filter by table
# print("\n--- Rules for employees table ---")
# emp_rules = get_rules_for_table("employees")
# for r in emp_rules:
#     print(f"  {r.rule_id}: {r.description}")

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

from src.rule_loader import load_rules
from src.validator import run_validation

rules = load_rules()
violations = run_validation(rules)

if violations.empty:
    print("No violations found!")
else:
    print(f"\nTotal violations found: {len(violations)}\n")
    print(violations.to_string(index=False))