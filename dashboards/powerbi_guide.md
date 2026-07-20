# Power BI Dashboard — Build Guide

Source files: `data/processed/dim_employee.csv`, `dim_date.csv`, `fact_payroll.csv`,
`fact_attendance_monthly.csv` (or connect directly to `database/payroll_analytics.db`
via the SQLite ODBC driver if you'd rather query live).

## 1. Import & model

1. **Get Data → Text/CSV**, import all four files from `data/processed/`.
2. Go to **Model view** and create these relationships (all `many-to-one`,
   single direction, from fact → dim):
   - `fact_payroll[employee_id]` → `dim_employee[employee_id]`
   - `fact_payroll[date_key]` → `dim_date[date_key]`
   - `fact_attendance_monthly[employee_id]` → `dim_employee[employee_id]`
   - `fact_attendance_monthly[date_key]` → `dim_date[date_key]`
3. Mark `dim_date` as a **Date table** (Modeling → Mark as date table →
   pick the `date` column).
4. Set data types: `netSalary`/`grossSalary`/etc. → Decimal Number,
   currency format `₹ #,##0`; `date_key` → Whole Number (hidden, it's a join
   key only — right-click → Hide in report view).

## 2. Measures (DAX) — put these in a new table called `_Measures`

```dax
Total Net Payroll = SUM(fact_payroll[netSalary])
Total Gross Payroll = SUM(fact_payroll[grossSalary])
Total Deductions = SUM(fact_payroll[totalDeductions])
Total LOP Cost = SUM(fact_payroll[lopDeduction])

Active Headcount =
CALCULATE(
    DISTINCTCOUNT(dim_employee[employee_id]),
    dim_employee[status] = "active"
)

Avg Net Salary = AVERAGE(fact_payroll[netSalary])

MoM Payroll Growth % =
VAR CurrentTotal = [Total Net Payroll]
VAR PriorTotal =
    CALCULATE([Total Net Payroll], DATEADD(dim_date[date], -1, MONTH))
RETURN DIVIDE(CurrentTotal - PriorTotal, PriorTotal)

Absenteeism Rate % =
DIVIDE(
    SUM(fact_attendance_monthly[absent]) + 0.5 * SUM(fact_attendance_monthly[half-day]),
    SUM(fact_attendance_monthly[days_recorded])
)

LOP % of Gross = DIVIDE([Total LOP Cost], [Total Gross Payroll])

YTD Net Payroll = TOTALYTD([Total Net Payroll], dim_date[date])
```

## 3. Dashboard pages

**Page 1 — Executive Summary**
- 4 KPI cards along the top: `Active Headcount`, `Total Net Payroll` (this
  month), `Absenteeism Rate %`, `MoM Payroll Growth %`.
- Line chart: `Total Net Payroll` by `dim_date[month]` (12-month trend).
- Bar chart: `Total Net Payroll` by `dim_employee[department]`.
- Add a **Forecast**: select the line chart → Analytics pane → Forecast →
  3 points forward, 95% confidence interval (Power BI's built-in
  exponential-smoothing forecast; the Python layer's linear-regression
  forecast in `python_analysis/summary_stats.json` is a good cross-check).

**Page 2 — Workforce**
- Donut: `Active Headcount` by department.
- Stacked bar: headcount by `tenure_bucket` (add a calculated column on
  `dim_employee`: `tenure_bucket = IF(DATEDIFF(dim_employee[date_of_joining], TODAY(), MONTH) < 12, "< 1 yr", ...)`).
- Table: top 10 earners YTD — `dim_employee[name]`, `dim_employee[department]`,
  `[YTD Net Payroll]`, sorted descending, Top N filter = 10.

**Page 3 — Attendance & Cost of Absence**
- Line chart: `[Absenteeism Rate %]` by month, with a department slicer.
- Scatter: department on X (or use a matrix), `[Absenteeism Rate %]` vs
  `[LOP % of Gross]` — this is the "does absenteeism actually cost us
  money" chart; the SQL/Python layers already show a strong positive
  correlation (see `query_results.md` §3a vs §2e).

## 4. Slicers (add to every page via a synced slicer panel)
- `dim_date[month_name]` (or a date range slicer)
- `dim_employee[department]`
- `dim_employee[status]`

## 5. Publish
File → Publish → Power BI Service, or Export → PDF for a static snapshot
to attach to the Word report.
