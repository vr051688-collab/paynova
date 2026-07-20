"""
Executes every query in analysis_queries.sql against the SQLite database,
saves each result as a CSV (database/query_results/*.csv) and stitches them
into a single Markdown file so the SQL layer's output is inspectable
without opening a DB client — and so 02_eda_and_trends.py / the report can
reuse these exact numbers instead of recomputing them differently.
"""
import os
import sqlite3
import pandas as pd

DB_PATH = "/home/claude/payroll-analytics/database/payroll_analytics.db"
OUT_DIR = "/home/claude/payroll-analytics/database/query_results"
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

QUERIES = {
    "1a_headcount_by_department": """
        SELECT department, COUNT(*) AS headcount,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM employees WHERE status='active'), 1) AS pct_of_workforce
        FROM employees WHERE status = 'active'
        GROUP BY department ORDER BY headcount DESC;
    """,
    "1b_headcount_trend_by_month": """
        WITH months AS (
            SELECT '2025-08' AS ym UNION SELECT '2025-09' UNION SELECT '2025-10' UNION SELECT '2025-11'
            UNION SELECT '2025-12' UNION SELECT '2026-01' UNION SELECT '2026-02' UNION SELECT '2026-03'
            UNION SELECT '2026-04' UNION SELECT '2026-05' UNION SELECT '2026-06' UNION SELECT '2026-07'
        )
        SELECT m.ym, COUNT(*) AS headcount_at_month_end
        FROM months m
        JOIN employees e ON e.date_of_joining <= (m.ym || '-28')
                        AND (e.exit_date IS NULL OR e.exit_date >= (m.ym || '-01'))
        GROUP BY m.ym ORDER BY m.ym;
    """,
    "1c_exits_by_month": """
        SELECT strftime('%Y-%m', exit_date) AS exit_month, COUNT(*) AS exits
        FROM employees WHERE exit_date IS NOT NULL
        GROUP BY exit_month ORDER BY exit_month;
    """,
    "1d_tenure_distribution": """
        SELECT CASE
                 WHEN tenure_months < 6 THEN '0-6 months' WHEN tenure_months < 12 THEN '6-12 months'
                 WHEN tenure_months < 24 THEN '1-2 years' WHEN tenure_months < 48 THEN '2-4 years'
                 ELSE '4+ years' END AS tenure_bucket,
               COUNT(*) AS employees
        FROM (SELECT employee_id, (julianday('2026-07-18') - julianday(date_of_joining)) / 30.44 AS tenure_months
              FROM employees WHERE status = 'active')
        GROUP BY tenure_bucket ORDER BY MIN(tenure_months);
    """,
    "2a_monthly_payroll_cost_trend": """
        SELECT year, month, ROUND(SUM(gross_salary),0) AS total_gross, ROUND(SUM(total_deductions),0) AS total_deductions,
               ROUND(SUM(net_salary),0) AS total_net, COUNT(*) AS payslips
        FROM payroll GROUP BY year, month ORDER BY year, month;
    """,
    "2b_department_cost_latest_month": """
        SELECT department, COUNT(*) AS headcount, ROUND(SUM(net_salary),0) AS total_net_cost,
               ROUND(AVG(net_salary),0) AS avg_net_salary
        FROM payroll WHERE year = 2026 AND month = 6
        GROUP BY department ORDER BY total_net_cost DESC;
    """,
    "2c_mom_payroll_growth": """
        WITH monthly AS (SELECT year, month, SUM(net_salary) AS total_net FROM payroll GROUP BY year, month)
        SELECT year, month, total_net,
               ROUND(100.0*(total_net - LAG(total_net) OVER (ORDER BY year,month)) / LAG(total_net) OVER (ORDER BY year,month), 2) AS mom_growth_pct
        FROM monthly ORDER BY year, month;
    """,
    "2d_top10_highest_cost_employees": """
        SELECT e.employee_id, e.name, e.department, e.designation, ROUND(SUM(p.net_salary),0) AS total_net_paid_ytd
        FROM payroll p JOIN employees e ON e.employee_id = p.employee_id
        GROUP BY e.employee_id ORDER BY total_net_paid_ytd DESC LIMIT 10;
    """,
    "2e_lop_impact_by_department": """
        SELECT department, ROUND(SUM(lop_deduction),0) AS total_lop,
               ROUND(SUM(lop_deduction)*100.0/SUM(gross_salary),2) AS lop_pct_of_gross
        FROM payroll GROUP BY department ORDER BY total_lop DESC;
    """,
    "3a_absenteeism_by_department": """
        SELECT e.department,
               ROUND(100.0*SUM(CASE WHEN a.status='absent' THEN 1 WHEN a.status='half-day' THEN 0.5 ELSE 0 END)/COUNT(*),2) AS absenteeism_rate_pct
        FROM attendance a JOIN employees e ON e.employee_id = a.employee_id
        GROUP BY e.department ORDER BY absenteeism_rate_pct DESC;
    """,
    "3b_absenteeism_seasonality": """
        SELECT strftime('%Y-%m', date) AS ym,
               ROUND(100.0*SUM(CASE WHEN status='absent' THEN 1 WHEN status='half-day' THEN 0.5 ELSE 0 END)/COUNT(*),2) AS absenteeism_rate_pct
        FROM attendance GROUP BY ym ORDER BY ym;
    """,
    "3c_chronic_absence_flag": """
        SELECT e.employee_id, e.name, e.department, COUNT(*) AS days_recorded,
               ROUND(100.0*SUM(CASE WHEN a.status='absent' THEN 1 WHEN a.status='half-day' THEN 0.5 ELSE 0 END)/COUNT(*),1) AS absenteeism_rate_pct
        FROM attendance a JOIN employees e ON e.employee_id = a.employee_id
        GROUP BY e.employee_id HAVING COUNT(*) >= 60
        ORDER BY absenteeism_rate_pct DESC LIMIT 15;
    """,
    "3d_friday_effect": """
        SELECT CASE WHEN strftime('%w', date) = '5' THEN 'Friday' ELSE 'Other weekday' END AS day_type,
               ROUND(100.0*SUM(CASE WHEN status='absent' THEN 1 WHEN status='half-day' THEN 0.5 ELSE 0 END)/COUNT(*),2) AS absence_rate_pct
        FROM attendance WHERE strftime('%w', date) NOT IN ('0') GROUP BY day_type;
    """,
    "4a_salary_bands": """
        SELECT department, designation, COUNT(*) AS headcount, MIN(basic_salary) AS min_basic,
               ROUND(AVG(basic_salary),0) AS avg_basic, MAX(basic_salary) AS max_basic
        FROM employees WHERE status='active'
        GROUP BY department, designation ORDER BY department, avg_basic DESC;
    """,
    "4b_statutory_load_by_department": """
        SELECT department, ROUND(SUM(pf)*100.0/SUM(gross_salary),2) AS pf_pct_of_gross,
               ROUND(SUM(professional_tax)*100.0/SUM(gross_salary),3) AS tax_pct_of_gross
        FROM payroll GROUP BY department ORDER BY pf_pct_of_gross DESC;
    """,
    "5a_new_hire_vs_tenured_pay": """
        SELECT CASE WHEN e.date_of_joining >= '2025-08-01' THEN 'Hired in analysis window' ELSE 'Tenured (pre-existing)' END AS cohort,
               COUNT(DISTINCT e.employee_id) AS headcount, ROUND(AVG(p.net_salary),0) AS avg_monthly_net
        FROM employees e JOIN payroll p ON p.employee_id = e.employee_id AND p.year=2026 AND p.month=6
        GROUP BY cohort;
    """,
}

md_lines = ["# SQL Analysis Results\n", "Generated from `analysis_queries.sql` against `payroll_analytics.db`.\n"]

for name, sql in QUERIES.items():
    df = pd.read_sql_query(sql, conn)
    df.to_csv(f"{OUT_DIR}/{name}.csv", index=False)
    md_lines.append(f"## {name}\n")
    md_lines.append(df.to_markdown(index=False))
    md_lines.append("\n")
    print(f"{name}: {len(df)} rows")

with open(f"{OUT_DIR}/../query_results.md", "w") as f:
    f.write("\n".join(md_lines))

conn.close()
print("\nAll query results saved to database/query_results/ and query_results.md")
