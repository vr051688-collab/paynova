# Payroll Analytics — Full Project

An end-to-end payroll analytics project: a live full-stack web app plus a SQL/Python data analysis layer covering headcount, payroll cost, attendance, and pay-equity insights.

## Structure

| Folder | What's inside |
|---|---|
| `app/` | MERN stack web app — login/logout, role-based dashboards (Admin & Employee), department cost & profit charts, employee salary management |
| `database/` | SQLite database, schema, and analysis SQL queries |
| `data/` | Raw and star-schema (fact/dimension) CSVs used for analysis |
| `analysis/` | Python scripts for data generation, EDA, trend forecasting, and star schema building |
| `charts/` | Generated chart images (headcount, payroll cost, absenteeism, tenure, forecasts) |
| `excel/` | Excel workbook version of the analytics, plus the script that builds it |
| `dashboards/` | Standalone HTML dashboard + guides for building the same dashboard in Tableau/Power BI |
| `analytics_csvs/` | Individual insight exports (headcount trends, exits, LOP impact, salary bands, etc.) |

## 1. Web App (`app/`)

A React + Express + MongoDB app with:
- JWT auth, bcrypt-hashed passwords
- Admin dashboard: department cost, profit stats, employee salaries, performance charts
- Employee dashboard: personal salary + performance view

See `app/SETUP_INSTRUCTIONS.md` for setup, seeding, and deployment (Vercel + Render).

## 2. Data Analysis (`database/`, `data/`, `analysis/`)

SQLite database (`database/payroll_analytics.db`) built from the CSVs in `data/`, with a star schema (`fact_payroll`, `fact_attendance_monthly`, `dim_date`, `dim_employee`) for analytical queries.

Run order (if regenerating from scratch):
1. `analysis/01_generate_data.py` — generates raw employee/payroll/attendance data
2. `database/build_database.py` — loads raw data into SQLite
3. `analysis/build_star_schema.py` — builds fact/dimension tables
4. `database/run_queries.py` — runs `database/analysis_queries.sql`, outputs to `database/query_results.md`
5. `analysis/02_eda_trends_forecast.py` — generates the charts in `charts/`
6. `analysis/build_dashboard_data.py` — builds `analysis/dashboard_data.json` for the HTML dashboard

## 3. Dashboards (`dashboards/`, `excel/`)

- `dashboards/dashboard.html` — standalone interactive HTML dashboard (open directly in browser)
- `excel/Payroll_Analytics_Workbook.xlsx` — the same analytics in Excel form
- `dashboards/tableau_guide.md` / `dashboards/powerbi_guide.md` — steps to rebuild the dashboard in Tableau or Power BI using the star schema

## Key insights covered

- Headcount by department & trend over time
- Monthly payroll cost trend + 3-month forecast
- Absenteeism seasonality and by-department breakdown
- Tenure distribution of active employees
- Top 10 earners (YTD net pay)
- Loss-of-pay (LOP) impact by department
- Salary bands and new-hire vs. tenured pay comparison
- Statutory load by department

---
Built by Aizen (Varun N) as a full-stack + data analytics portfolio project.
