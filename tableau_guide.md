# Tableau Dashboard — Build Guide

Source files: same star schema as the Power BI guide —
`data/processed/dim_employee.csv`, `dim_date.csv`, `fact_payroll.csv`,
`fact_attendance_monthly.csv`.

## 1. Connect & relate

1. **Connect → Text File**, add all four CSVs to the canvas.
2. Use Tableau's **Relationships** (not legacy joins, so grains don't get
   flattened):
   - `fact_payroll` ⟷ `dim_employee` on `employee_id`
   - `fact_payroll` ⟷ `dim_date` on `date_key`
   - `fact_attendance_monthly` ⟷ `dim_employee` on `employee_id`
   - `fact_attendance_monthly` ⟷ `dim_date` on `date_key`
3. On each connection, verify cardinality shows *-1 (fact side many, dim
   side one) — Tableau infers this automatically but double-check it didn't
   guess wrong on `date_key`.
4. Rename the fields with the friendly labels analysts will actually type:
   `netSalary` → `Net Salary`, `grossSalary` → `Gross Salary`, etc.

## 2. Calculated fields

```
// Absenteeism Rate %
([absent] + 0.5 * [half-day]) / [days_recorded]

// LOP % of Gross  (build on fact_payroll)
SUM([lopDeduction]) / SUM([grossSalary])

// MoM Payroll Growth %
(ZN(SUM([netSalary])) - LOOKUP(ZN(SUM([netSalary])), -1))
/ ABS(LOOKUP(ZN(SUM([netSalary])), -1))
// set the table calculation's "Compute Using" to the month field, sorted chronologically

// Tenure (months)
DATEDIFF('month', [date_of_joining], TODAY())

// Tenure Bucket
IF [Tenure (months)] < 6 THEN "0-6 mo"
ELSEIF [Tenure (months)] < 12 THEN "6-12 mo"
ELSEIF [Tenure (months)] < 24 THEN "1-2 yr"
ELSEIF [Tenure (months)] < 48 THEN "2-4 yr"
ELSE "4+ yr" END
```

## 3. Sheets → Dashboard

**Sheet: Payroll Trend**
- Columns: `MONTH(date)` (from `dim_date`, continuous). Rows: `SUM(Net Salary)`.
- Right-click the trend line → **Add Forecast** (Analytics pane, drag
  "Forecast" onto the view). Tableau's exponential smoothing forecast will
  extend the line 3-4 periods forward with a confidence band — a nice
  visual pair with the scikit-learn forecast in the Python report (which
  gives you the R² Tableau's forecast pane doesn't surface).

**Sheet: Department Cost** — Bar chart, `Department` on Rows, `SUM(Net Salary)`
on Columns, sorted descending. Color by department for consistency across
sheets (right-click the Department field → Default Properties → Color).

**Sheet: Headcount Donut** — Pie/donut of `COUNTD(employee_id)` by
`Department`, filtered to `status = "active"`.

**Sheet: Absenteeism vs LOP Cost** — Dual-axis or scatter:
`Department` on Rows/color, `Absenteeism Rate %` and `LOP % of Gross` as two
measures — this is the key "attendance problems cost real money" chart.

**Sheet: Top Earners** — Horizontal bar, `SUM(Net Salary)` (YTD, filter date
range to the full 12 months), Top 10 filter on `employee_id` by that
measure.

**Dashboard: Executive Summary**
- Combine Payroll Trend + Department Cost + Headcount Donut + 3-4 KPI text
  boxes (Active Headcount, Total Net Payroll MTD, Absenteeism Rate %,
  MoM Growth %) built from the calculated fields above.
- Add a **Department** filter and a **Date Range** filter, applied to all
  sheets via "Apply to Worksheets → All Using This Data Source".

## 4. Publish
Server → Publish Workbook (Tableau Server/Cloud), or Dashboard → Export
Image/PDF for a static snapshot to attach to the Word report.
