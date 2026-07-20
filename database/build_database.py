"""
Loads the generated CSVs into a SQLite database with proper types, keys,
and indexes — this is the file the SQL analysis queries run against, and
what Power BI / Tableau / Excel can all connect to directly.
"""
import sqlite3
import pandas as pd

DB_PATH = "/home/claude/payroll-analytics/database/payroll_analytics.db"
RAW = "/home/claude/payroll-analytics/data/raw"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript(
    """
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS attendance;
    DROP TABLE IF EXISTS payroll;

    CREATE TABLE employees (
        employee_id      TEXT PRIMARY KEY,
        name             TEXT NOT NULL,
        email            TEXT NOT NULL,
        phone            TEXT,
        department       TEXT NOT NULL,
        designation      TEXT NOT NULL,
        date_of_joining  TEXT NOT NULL,
        exit_date        TEXT,
        status           TEXT NOT NULL CHECK (status IN ('active','inactive')),
        basic_salary     REAL NOT NULL,
        da_percent       REAL NOT NULL,
        hra_percent      REAL NOT NULL,
        other_allowances REAL NOT NULL,
        pf_percent       REAL NOT NULL,
        professional_tax REAL NOT NULL
    );

    CREATE TABLE attendance (
        employee_id TEXT NOT NULL,
        date        TEXT NOT NULL,
        status      TEXT NOT NULL CHECK (status IN ('present','absent','half-day','leave')),
        PRIMARY KEY (employee_id, date),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

    CREATE TABLE payroll (
        employee_id       TEXT NOT NULL,
        department        TEXT NOT NULL,
        month             INTEGER NOT NULL,
        year              INTEGER NOT NULL,
        working_days      INTEGER NOT NULL,
        present_days      INTEGER NOT NULL,
        absent_days       INTEGER NOT NULL,
        half_days         INTEGER NOT NULL,
        leave_days        INTEGER NOT NULL,
        basic_salary      REAL NOT NULL,
        da                REAL NOT NULL,
        hra               REAL NOT NULL,
        other_allowances  REAL NOT NULL,
        gross_salary      REAL NOT NULL,
        pf                REAL NOT NULL,
        professional_tax  REAL NOT NULL,
        lop_deduction     REAL NOT NULL,
        total_deductions  REAL NOT NULL,
        net_salary        REAL NOT NULL,
        status            TEXT NOT NULL,
        PRIMARY KEY (employee_id, year, month),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

    CREATE INDEX idx_attendance_date ON attendance(date);
    CREATE INDEX idx_attendance_status ON attendance(status);
    CREATE INDEX idx_payroll_year_month ON payroll(year, month);
    CREATE INDEX idx_payroll_department ON payroll(department);
    CREATE INDEX idx_employees_department ON employees(department);
    CREATE INDEX idx_employees_status ON employees(status);
    """
)

employees_df = pd.read_csv(f"{RAW}/employees.csv")
employees_df = employees_df.rename(
    columns={
        "employeeId": "employee_id", "dateOfJoining": "date_of_joining", "exitDate": "exit_date",
        "basicSalary": "basic_salary", "daPercent": "da_percent", "hraPercent": "hra_percent",
        "otherAllowances": "other_allowances", "pfPercent": "pf_percent", "professionalTax": "professional_tax",
    }
)
employees_df["exit_date"] = employees_df["exit_date"].replace("", None)
employees_df.to_sql("employees", conn, if_exists="append", index=False)

attendance_df = pd.read_csv(f"{RAW}/attendance.csv").rename(columns={"employeeId": "employee_id"})
attendance_df.to_sql("attendance", conn, if_exists="append", index=False)

payroll_df = pd.read_csv(f"{RAW}/payroll.csv").rename(
    columns={
        "employeeId": "employee_id", "workingDays": "working_days", "presentDays": "present_days",
        "absentDays": "absent_days", "halfDays": "half_days", "leaveDays": "leave_days",
        "basicSalary": "basic_salary", "otherAllowances": "other_allowances", "grossSalary": "gross_salary",
        "professionalTax": "professional_tax", "lopDeduction": "lop_deduction",
        "totalDeductions": "total_deductions", "netSalary": "net_salary",
    }
)
payroll_df.to_sql("payroll", conn, if_exists="append", index=False)

conn.commit()

counts = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ["employees", "attendance", "payroll"]}
print("Row counts:", counts)

with open("/home/claude/payroll-analytics/database/schema.sql", "w") as f:
    for row in cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table','index') AND sql IS NOT NULL"):
        f.write(row[0] + ";\n\n")

conn.close()
print("Database built:", DB_PATH)
