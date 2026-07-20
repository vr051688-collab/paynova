"""
Generates a realistic synthetic dataset matching the Payroll System's schema
(Employee / Attendance / Payroll, as defined in backend/models/*.js) so the
rest of the analytics project has real, patterned data to work with instead
of a bare 2-row seed.

Output: data/raw/employees.csv, attendance.csv, payroll.csv

Design choices (so the analysis below has something real to find):
 - 185 employees across 7 departments with realistic designation/salary bands.
 - Hiring spread over the past ~3 years, plus a resignation trickle so
   headcount and attrition trends exist.
 - Attendance has real structure: Sales/Support run higher absenteeism,
   October-November (festival season) and monsoon months dip attendance
   company-wide, and there's a mild "Friday effect."
 - Payroll is computed with the exact same formula as
   backend/utils/payrollCalculator.js, including an April increment cycle,
   so SQL/Python results are internally consistent with the live app.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# 1. Employees
# ---------------------------------------------------------------------------
DEPARTMENTS = {
    "Engineering": {
        "designations": ["Software Engineer", "Senior Software Engineer", "QA Engineer", "DevOps Engineer", "Engineering Manager"],
        "basic_range": (38000, 95000),
        "headcount_weight": 0.28,
    },
    "Sales": {
        "designations": ["Sales Executive", "Senior Sales Executive", "Sales Manager", "Business Development Associate"],
        "basic_range": (26000, 70000),
        "headcount_weight": 0.20,
    },
    "Marketing": {
        "designations": ["Marketing Associate", "Content Strategist", "SEO Specialist", "Marketing Manager"],
        "basic_range": (28000, 65000),
        "headcount_weight": 0.10,
    },
    "Operations": {
        "designations": ["Operations Executive", "Operations Analyst", "Operations Manager"],
        "basic_range": (27000, 60000),
        "headcount_weight": 0.12,
    },
    "Finance": {
        "designations": ["Accounts Executive", "Financial Analyst", "Finance Manager"],
        "basic_range": (30000, 75000),
        "headcount_weight": 0.10,
    },
    "HR": {
        "designations": ["HR Executive", "Talent Acquisition Specialist", "HR Manager"],
        "basic_range": (26000, 62000),
        "headcount_weight": 0.08,
    },
    "Support": {
        "designations": ["Support Associate", "Senior Support Associate", "Support Team Lead"],
        "basic_range": (22000, 48000),
        "headcount_weight": 0.12,
    },
}

FIRST_NAMES = [
    "Asha", "Karthik", "Priya", "Arjun", "Divya", "Rohan", "Sneha", "Vikram", "Ananya", "Rahul",
    "Meera", "Siddharth", "Kavya", "Aditya", "Pooja", "Nikhil", "Shreya", "Manish", "Aishwarya", "Varun",
    "Deepika", "Suresh", "Lakshmi", "Ganesh", "Nisha", "Rajesh", "Swathi", "Vivek", "Ramya", "Harish",
    "Anjali", "Kiran", "Sowmya", "Prakash", "Neha", "Sanjay", "Divya", "Abhishek", "Preethi", "Manoj",
    "Yamini", "Naveen", "Bhavana", "Sathish", "Chitra", "Girish", "Padma", "Ravi", "Sunita", "Ashok",
]
LAST_NAMES = [
    "Rao", "Iyer", "Nair", "Reddy", "Sharma", "Gupta", "Kumar", "Menon", "Pillai", "Verma",
    "Naidu", "Shetty", "Hegde", "Bhat", "Gowda", "Patil", "Desai", "Joshi", "Kulkarni", "Bose",
]

TODAY = date(2026, 7, 18)
DATA_START = date(2025, 8, 1)  # 12-month analysis window: Aug 2025 - Jul 2026
HIRE_WINDOW_START = date(2022, 6, 1)  # some employees pre-date the analysis window

N_EMPLOYEES = 185
dept_names = list(DEPARTMENTS.keys())
dept_weights = np.array([DEPARTMENTS[d]["headcount_weight"] for d in dept_names])
dept_weights = dept_weights / dept_weights.sum()

employees = []
used_names = set()
for i in range(1, N_EMPLOYEES + 1):
    dept = rng.choice(dept_names, p=dept_weights)
    spec = DEPARTMENTS[dept]
    designation = rng.choice(spec["designations"])
    lo, hi = spec["basic_range"]
    basic_salary = round(float(rng.triangular(lo, lo + (hi - lo) * 0.35, hi)) / 500) * 500

    while True:
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        if name not in used_names:
            used_names.add(name)
            break

    total_days = (TODAY - HIRE_WINDOW_START).days
    hire_offset = int(rng.triangular(0, total_days * 0.55, total_days))
    hire_date = HIRE_WINDOW_START + timedelta(days=hire_offset)

    is_leaver = rng.random() < 0.09 and hire_date < date(2026, 4, 1)
    exit_date = None
    if is_leaver:
        earliest_exit = max(hire_date + timedelta(days=180), DATA_START)
        latest_exit = date(2026, 6, 30)
        if earliest_exit < latest_exit:
            exit_offset = int(rng.uniform(0, (latest_exit - earliest_exit).days))
            exit_date = earliest_exit + timedelta(days=exit_offset)

    status = "inactive" if exit_date else "active"

    employees.append(
        {
            "employeeId": f"EMP{i:04d}",
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}{i}@example.com",
            "phone": f"9{rng.integers(100000000, 999999999)}",
            "department": dept,
            "designation": designation,
            "dateOfJoining": hire_date.isoformat(),
            "exitDate": exit_date.isoformat() if exit_date else "",
            "status": status,
            "basicSalary": basic_salary,
            "daPercent": 12,
            "hraPercent": 10,
            "otherAllowances": int(rng.choice([0, 1000, 1500, 2000, 2500], p=[0.35, 0.25, 0.2, 0.12, 0.08])),
            "pfPercent": 12,
            "professionalTax": 200,
        }
    )

employees_df = pd.DataFrame(employees)
employees_df.to_csv("/home/claude/payroll-analytics/data/raw/employees.csv", index=False)
print(f"Employees: {len(employees_df)} rows | active={sum(employees_df.status=='active')} inactive={sum(employees_df.status=='inactive')}")

# ---------------------------------------------------------------------------
# 2. Attendance (daily, Aug 2025 - Jul 2026, all days except Sunday — matches
#    getWorkingDaysInMonth() in payrollController.js)
# ---------------------------------------------------------------------------
MONTHS = pd.date_range(DATA_START, periods=12, freq="MS")

DEPT_ABSENCE_BIAS = {
    "Sales": 1.35, "Support": 1.25, "Marketing": 1.05, "Operations": 1.0,
    "Engineering": 0.85, "Finance": 0.8, "HR": 0.9,
}
SEASONAL_BIAS = {8: 1.0, 9: 1.0, 10: 1.4, 11: 1.3, 12: 1.05, 1: 0.95,
                  2: 0.9, 3: 0.95, 4: 1.0, 5: 1.05, 6: 1.15, 7: 1.2}

attendance_rows = []
emp_records = employees_df.to_dict("records")

for emp in emp_records:
    hire = date.fromisoformat(emp["dateOfJoining"])
    exit_ = date.fromisoformat(emp["exitDate"]) if emp["exitDate"] else None
    bias = DEPT_ABSENCE_BIAS.get(emp["department"], 1.0)
    personal_reliability = rng.normal(1.0, 0.18)

    for month_start in MONTHS:
        y, m = month_start.year, month_start.month
        days_in_month = pd.Period(f"{y}-{m:02d}").days_in_month
        seasonal = SEASONAL_BIAS[m]

        for d in range(1, days_in_month + 1):
            the_date = date(y, m, d)
            if the_date.weekday() == 6:
                continue
            if the_date < hire or the_date > TODAY:
                continue
            if exit_ and the_date > exit_:
                continue

            friday_effect = 1.15 if the_date.weekday() == 4 else 1.0
            p_absent_family = min(
                0.16, 0.045 * bias * seasonal * friday_effect * max(personal_reliability, 0.4)
            )
            roll = rng.random()
            if roll < p_absent_family * 0.55:
                status = "absent"
            elif roll < p_absent_family:
                status = "half-day"
            elif roll < p_absent_family + 0.02:
                status = "leave"
            else:
                status = "present"

            attendance_rows.append(
                {"employeeId": emp["employeeId"], "date": the_date.isoformat(), "status": status}
            )

attendance_df = pd.DataFrame(attendance_rows)
attendance_df.to_csv("/home/claude/payroll-analytics/data/raw/attendance.csv", index=False)
print(f"Attendance: {len(attendance_df):,} rows across {attendance_df['employeeId'].nunique()} employees")

# ---------------------------------------------------------------------------
# 3. Payroll — recomputed monthly using the identical formula to
#    backend/utils/payrollCalculator.js, including an April increment cycle.
# ---------------------------------------------------------------------------
def working_days_in_month(year, month):
    days_in_month = pd.Period(f"{year}-{month:02d}").days_in_month
    count = 0
    for d in range(1, days_in_month + 1):
        if date(year, month, d).weekday() != 6:
            count += 1
    return count


def round2(x):
    return round(x + 1e-9, 2)


att_by_emp_month = (
    attendance_df.assign(
        year=lambda d: pd.to_datetime(d["date"]).dt.year,
        month=lambda d: pd.to_datetime(d["date"]).dt.month,
    )
    .groupby(["employeeId", "year", "month", "status"])
    .size()
    .unstack(fill_value=0)
)
for col in ["present", "absent", "half-day", "leave"]:
    if col not in att_by_emp_month.columns:
        att_by_emp_month[col] = 0

payroll_rows = []
for emp in emp_records:
    hire = date.fromisoformat(emp["dateOfJoining"])
    exit_ = date.fromisoformat(emp["exitDate"]) if emp["exitDate"] else None
    basic = emp["basicSalary"]

    for month_start in MONTHS:
        y, m = month_start.year, month_start.month
        month_last_day = date(y, m, pd.Period(f"{y}-{m:02d}").days_in_month)
        if month_last_day < hire:
            continue
        if exit_ and date(y, m, 1) > exit_:
            continue

        eff_basic = basic
        if (y, m) >= (2026, 4) and hire <= date(2025, 4, 1):
            eff_basic = round(basic * float(rng.uniform(1.06, 1.14)) / 500) * 500

        working_days = working_days_in_month(y, m)
        try:
            att = att_by_emp_month.loc[(emp["employeeId"], y, m)]
            absent_days, half_days = int(att["absent"]), int(att["half-day"])
            leave_days = int(att["leave"])
        except KeyError:
            absent_days = half_days = leave_days = 0
        present_days = working_days - absent_days - half_days - leave_days

        da = round2(0.12 * eff_basic)
        hra = round2(0.10 * eff_basic)
        other = emp["otherAllowances"]
        gross = round2(eff_basic + da + hra + other)
        pf = round2(0.12 * (eff_basic + da))
        prof_tax = emp["professionalTax"]
        effective_absent_units = absent_days + half_days * 0.5
        per_day_gross = gross / working_days if working_days else 0
        lop = round2(per_day_gross * effective_absent_units)
        total_deductions = round2(pf + prof_tax + lop)
        net = round2(gross - total_deductions)

        payroll_rows.append(
            {
                "employeeId": emp["employeeId"], "department": emp["department"], "month": m, "year": y,
                "workingDays": working_days, "presentDays": present_days, "absentDays": absent_days,
                "halfDays": half_days, "leaveDays": leave_days, "basicSalary": eff_basic, "da": da, "hra": hra,
                "otherAllowances": other, "grossSalary": gross, "pf": pf, "professionalTax": prof_tax,
                "lopDeduction": lop, "totalDeductions": total_deductions, "netSalary": net,
                "status": "paid" if (y, m) < (2026, 7) else "generated",
            }
        )

payroll_df = pd.DataFrame(payroll_rows)
payroll_df.to_csv("/home/claude/payroll-analytics/data/raw/payroll.csv", index=False)
print(f"Payroll: {len(payroll_df):,} payslips | total net paid = Rs {payroll_df['netSalary'].sum():,.0f}")
