import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sample.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id   INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL
);

CREATE TABLE employees (
    emp_id     INTEGER PRIMARY KEY,
    name       TEXT,
    email      TEXT,
    age        INTEGER,
    salary     REAL,
    dept_id    INTEGER,
    status     TEXT
);

INSERT INTO departments VALUES (1,'Engineering'),(2,'HR'),(3,'Finance');

INSERT INTO employees VALUES
(1,  'Rahul Sharma',   'rahul@company.com',   32, 75000, 1, 'active'),
(2,  'Priya Mehta',    'priya@company.com',   28, 62000, 2, 'active'),
(3,  'Amit Joshi',     NULL,                  25, 48000, 1, 'active'),
(4,  'Sneha Patil',    'sneha@company.com',   -5, 55000, 2, 'active'),
(5,  'Ravi Kumar',     'ravi@company.com',    29, 999999,3, 'active'),
(6,  'Neha Singh',     'neha@company.com',    31, 61000, 9, 'active'),
(7,  NULL,             'no_name@company.com', 27, 58000, 1, 'active'),
(8,  'Priya Mehta',    'priya@company.com',   28, 62000, 2, 'active'),
(9,  'Suresh Rao',     'not-an-email',        45, 70000, 3, 'active'),
(10, 'Kavita Desai',   'kavita@company.com',  30, NULL,  1, 'unknown');
""")

conn.commit()
conn.close()
print(f"Sample DB created at: {DB_PATH}")