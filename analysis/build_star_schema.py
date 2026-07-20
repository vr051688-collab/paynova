"""
Builds a star schema from the raw data — one fact table for payroll, one for
attendance rolled up to monthly (daily-grain attendance is 52k+ rows, too
granular to be a useful Power BI/Tableau fact table on its own), and
dimension tables for employee and date. This is the exact shape Power BI /
Tableau expect: skinny fact tables with foreign keys, wide dimension tables
with the descriptive attributes to slice by.
"""
import pandas as pd

RAW = "/home/claude/payroll-analytics/data/raw"
OUT = "/home/claude/payroll-analytics/data/processed"

employees = pd.read_csv(f"{RAW}/employees.csv")
attendance = pd.read_csv(f"{RAW}/attendance.csv", parse_dates=["date"])
payroll = pd.read_csv(f"{RAW}/payroll.csv")

# ---- dim_employee -----------------------------------------------------------
dim_employee = employees.rename(columns={"employeeId": "employee_id"})[
    ["employee_id", "name", "department", "designation", "dateOfJoining", "exitDate", "status",
     "basicSalary", "otherAllowances"]
].rename(columns={"dateOfJoining": "date_of_joining", "exitDate": "exit_date", "basicSalary": "current_basic_salary",
                   "otherAllowances": "other_allowances"})
dim_employee.to_csv(f"{OUT}/dim_employee.csv", index=False)

# ---- dim_date (one row per calendar day in the analysis window) ------------
all_days = pd.date_range("2025-08-01", "2026-07-31", freq="D")
dim_date = pd.DataFrame({"date": all_days})
dim_date["date_key"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.strftime("%B")
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["day_of_week"] = dim_date["date"].dt.day_name()
dim_date["is_working_day"] = dim_date["date"].dt.dayofweek != 6  # matches app's Sunday-off rule
dim_date = dim_date[["date_key", "date", "year", "month", "month_name", "quarter", "day_of_week", "is_working_day"]]
dim_date.to_csv(f"{OUT}/dim_date.csv", index=False)

# ---- fact_payroll (grain: one row per employee per month) ------------------
fact_payroll = payroll.rename(columns={"employeeId": "employee_id"})
fact_payroll["date_key"] = (fact_payroll["year"].astype(str) + fact_payroll["month"].astype(str).str.zfill(2) + "01").astype(int)
fact_payroll = fact_payroll[
    ["employee_id", "department", "date_key", "year", "month", "workingDays", "presentDays", "absentDays",
     "halfDays", "leaveDays", "basicSalary", "da", "hra", "otherAllowances", "grossSalary", "pf",
     "professionalTax", "lopDeduction", "totalDeductions", "netSalary", "status"]
]
fact_payroll.to_csv(f"{OUT}/fact_payroll.csv", index=False)

# ---- fact_attendance_monthly (grain: employee x month x status count) ------
attendance["date_key"] = attendance["date"].dt.strftime("%Y%m") + "01"
attendance["date_key"] = attendance["date_key"].astype(int)
fact_attendance_monthly = (
    attendance.assign(year=attendance["date"].dt.year, month=attendance["date"].dt.month)
    .groupby(["employeeId", "year", "month", "status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
    .rename(columns={"employeeId": "employee_id"})
)
for col in ["present", "absent", "half-day", "leave"]:
    if col not in fact_attendance_monthly.columns:
        fact_attendance_monthly[col] = 0
fact_attendance_monthly["date_key"] = (
    fact_attendance_monthly["year"].astype(str) + fact_attendance_monthly["month"].astype(str).str.zfill(2) + "01"
).astype(int)
fact_attendance_monthly["days_recorded"] = fact_attendance_monthly[["present", "absent", "half-day", "leave"]].sum(axis=1)
fact_attendance_monthly["absenteeism_rate_pct"] = (
    (fact_attendance_monthly["absent"] + 0.5 * fact_attendance_monthly["half-day"])
    / fact_attendance_monthly["days_recorded"] * 100
).round(2)
fact_attendance_monthly.to_csv(f"{OUT}/fact_attendance_monthly.csv", index=False)

print("Star schema written to", OUT)
for name, df in [("dim_employee", dim_employee), ("dim_date", dim_date),
                  ("fact_payroll", fact_payroll), ("fact_attendance_monthly", fact_attendance_monthly)]:
    print(f"  {name}: {df.shape[0]} rows x {df.shape[1]} cols")
