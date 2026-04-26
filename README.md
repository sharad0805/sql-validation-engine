# SQL Data Validation & Reporting Engine

A configurable Python + SQL engine that automatically validates database tables
against defined rules, detects data anomalies, and generates color-coded Excel reports.

Built to simulate real-world data quality workflows used in production backend systems.

---

## Why this project exists

Manual data validation across database tables is:
- Error-prone and inconsistent
- Time-consuming for QA and backend teams
- Hard to track and report to stakeholders

This tool automates the entire process — define your rules once in a YAML config,
run the engine, get a report. No hardcoded logic. No manual checking.

---

## Features

- 6 validation rule types — null, range, regex, allowed values, uniqueness, referential
- Config-driven rules via YAML — add new rules without touching Python code
- Color-coded Excel report — critical (red), high (orange), medium (yellow)
- Two-sheet report — executive summary + full violations detail
- CLI with flags — filter by table, severity, dry-run mode
- Structured logging — every run saved to logs/ with timestamp
- DB agnostic — works with SQLite, MySQL, Oracle via SQLAlchemy
- Exit code 1 on critical violations — CI/CD pipeline friendly

---

## Tech stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Language     | Python 3.11+                      |
| DB Layer     | SQLAlchemy                        |
| Data         | Pandas                            |
| Rules config | PyYAML                            |
| Reporting    | openpyxl                          |
| CLI          | argparse                          |
| Databases    | SQLite / MySQL / Oracle           |

---

## Project structure
sql-validation-engine/
├── config/
│   ├── db_config.yaml       # DB connection settings
│   └── rules.yaml           # All validation rules
├── src/
│   ├── db_connector.py      # SQLAlchemy engine + query runner
│   ├── rule_loader.py       # Parses rules.yaml into Rule objects
│   ├── validator.py         # Core rule engine - detects violations
│   ├── anomaly_detector.py  # Duplicate, outlier, schema drift detection
│   └── report_generator.py  # Styled Excel report builder
├── sample_data/
│   ├── create_db.py         # Script to generate sample SQLite DB
│   └── sample.db            # SQLite DB with intentional dirty data
├── reports/                 # Auto-generated reports (git ignored)
├── logs/                    # Run logs with timestamps (git ignored)
├── main.py                  # CLI entry point
└── requirements.txt

---

## Quickstart

### 1. Clone and set up

```bash
git clone https://github.com/YOUR_USERNAME/sql-validation-engine.git
cd sql-validation-engine

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Create the sample database

```bash
python sample_data/create_db.py
```

### 3. Run validation

```bash
# Full validation - all tables, Excel report
python main.py

# Validate a specific table only
python main.py --table employees

# Show only critical violations
python main.py --severity critical

# Dry run - validate without saving report
python main.py --dry-run

# Help - see all options
python main.py --help
```

---

## Sample output

### Console summary
=======================================================
VALIDATION SUMMARY
Total rules run   : 9
Total violations  : 10
Critical          : 3
High              : 5
Medium            : 2
TOP VIOLATIONS:
[CRITICAL] R001 | employees.name    | Row 7  | Value: None
[CRITICAL] R003 | employees.salary  | Row 10 | Value: None
[CRITICAL] R009 | employees.dept_id | Row 6  | Value: 9
[HIGH    ] R002 | employees.email   | Row 3  | Value: None
[HIGH    ] R005 | employees.salary  | Row 5  | Value: 999999.0
[MEDIUM  ] R006 | employees.email   | Row 9  | Value: not-an-email

### Excel report — Summary sheet

| Severity | Count | Rules Affected |
|----------|-------|----------------|
| CRITICAL | 3     | 3              |
| HIGH     | 5     | 3              |
| MEDIUM   | 2     | 2              |

### Excel report — All Violations sheet

Color-coded rows by severity with full details:
Rule ID, Table, Column, Rule Type, Severity, Row ID, Violated Value, Description.

---

## Defining validation rules

Rules live in `config/rules.yaml`. No Python changes needed to add a new rule.

```yaml
rules:
  - rule_id: R001
    table: employees
    column: name
    rule_type: null_check
    severity: critical
    description: "Employee name must not be null"

  - rule_id: R004
    table: employees
    column: age
    rule_type: range_check
    params:
      min: 18
      max: 65
    severity: high
    description: "Employee age must be between 18 and 65"

  - rule_id: R006
    table: employees
    column: email
    rule_type: regex_check
    params:
      pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w{2,}$"
    severity: medium
    description: "Email must be in valid format"
```

### Supported rule types

| Rule Type            | Description                                      |
|----------------------|--------------------------------------------------|
| null_check           | Flags rows where column value is NULL            |
| range_check          | Flags values outside defined min/max bounds      |
| regex_check          | Flags values not matching a regex pattern        |
| allowed_values_check | Flags values not in a defined allowed list       |
| uniqueness_check     | Flags duplicate values in a column               |
| referential_check    | Flags values not found in a referenced table     |

---

## Connecting to MySQL or Oracle

Update `config/db_config.yaml`:

```yaml
# MySQL
database:
  type: mysql
  host: localhost
  port: 3306
  username: root
  password: yourpassword
  database: your_db_name

# Oracle
database:
  type: oracle
  host: localhost
  port: 1521
  username: system
  password: yourpassword
  service_name: XEPDB1
```

No changes needed in Python code — the engine picks up the config automatically.

---

## Requirements
sqlalchemy
pandas
openpyxl
pyyaml
reportlab

Install with:
```bash
pip install -r requirements.txt
```

---

## Author

**Sharad Sambare**
Python Developer | TCS
[LinkedIn](https://linkedin.com/in/sharad-sambare-6368a7216) | [GitHub](https://github.com/sharad0805)