-- ============================================================================
-- Payroll Analytics — SQL Analysis Queries
-- Run against: database/payroll_analytics.db (SQLite)
-- Also portable to MySQL/Postgres with minor syntax tweaks (noted where it
-- matters — SQLite's strftime() vs. EXTRACT()/DATE_TRUNC() being the main one).
-- ============================================================================

-- 1. Headcount & workforce composition -------------------------------------

-- 1a. Current headcount by department (active employees only)
SELECT department,
       COUNT(*) AS headcount,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM employees WHERE status = 'active'), 1) AS pct_of_workforce
FROM employees
WHERE status = 'active'
GROUP BY department
ORDER BY headcount DESC;

-- 1b. Headcount trend by month (net of joiners/leavers) — cumulative
--     active headcount as of the last day of each month in the window.
WITH months AS (
    SELECT '2025-08' AS ym UNION SELECT '2025-09' UNION SELECT '2025-10' UNION SELECT '2025-11'
    UNION SELECT '2025-12' UNION SELECT '2026-01' UNION SELECT '2026-02' UNION SELECT '2026-03'
    UNION SELECT '2026-04' UNION SELECT '2026-05' UNION SELECT '2026-06' UNION SELECT '2026-07'
)
SELECT m.ym,
       COUNT(*) AS headcount_at_month_end
FROM months m
JOIN employees e
  ON e.date_of_joining <= (m.ym || '-28')
 AND (e.exit_date IS NULL OR e.exit_date >= (m.ym || '-01'))
GROUP BY m.ym
ORDER BY m.ym;

-- 1c. Attrition rate: exits per month vs. average active headcount
SELECT strftime('%Y-%m', exit_date) AS exit_month,
       COUNT(*) AS exits
FROM employees
WHERE exit_date IS NOT NULL
GROUP BY exit_month
ORDER BY exit_month;

-- 1d. Tenure distribution of current active employees (in months, as of today)
SELECT
    CASE
        WHEN tenure_months < 6  THEN '0-6 months'
        WHEN tenure_months < 12 THEN '6-12 months'
        WHEN tenure_months < 24 THEN '1-2 years'
        WHEN tenure_months < 48 THEN '2-4 years'
        ELSE '4+ years'
    END AS tenure_bucket,
    COUNT(*) AS employees
FROM (
    SELECT employee_id,
           (julianday('2026-07-18') - julianday(date_of_joining)) / 30.44 AS tenure_months
    FROM employees
    WHERE status = 'active'
)
GROUP BY tenure_bucket
ORDER BY MIN(tenure_months);

-- 2. Payroll cost analysis ---------------------------------------------------

-- 2a. Monthly company-wide payroll cost trend (gross vs net vs deductions)
SELECT year, month,
       ROUND(SUM(gross_salary), 0)     AS total_gross,
       ROUND(SUM(total_deductions), 0) AS total_deductions,
       ROUND(SUM(net_salary), 0)       AS total_net,
       COUNT(*)                        AS payslips
FROM payroll
GROUP BY year, month
ORDER BY year, month;

-- 2b. Department-wise payroll cost and average net salary (latest month)
SELECT department,
       COUNT(*)                    AS headcount,
       ROUND(SUM(net_salary), 0)   AS total_net_cost,
       ROUND(AVG(net_salary), 0)   AS avg_net_salary
FROM payroll
WHERE year = 2026 AND month = 6   -- last fully "paid" month in the dataset
GROUP BY department
ORDER BY total_net_cost DESC;

-- 2c. Month-over-month payroll cost growth (%)
WITH monthly AS (
    SELECT year, month, SUM(net_salary) AS total_net
    FROM payroll
    GROUP BY year, month
)
SELECT year, month, total_net,
       ROUND(
         100.0 * (total_net - LAG(total_net) OVER (ORDER BY year, month))
         / LAG(total_net) OVER (ORDER BY year, month), 2
       ) AS mom_growth_pct
FROM monthly
ORDER BY year, month;

-- 2d. Top 10 highest-cost employees over the full year (by total net paid)
SELECT e.employee_id, e.name, e.department, e.designation,
       ROUND(SUM(p.net_salary), 0) AS total_net_paid_ytd
FROM payroll p
JOIN employees e ON e.employee_id = p.employee_id
GROUP BY e.employee_id
ORDER BY total_net_paid_ytd DESC
LIMIT 10;

-- 2e. Loss-of-pay (LOP) impact — how much absenteeism actually costs, by department
SELECT department,
       ROUND(SUM(lop_deduction), 0)                       AS total_lop,
       ROUND(SUM(lop_deduction) * 100.0 / SUM(gross_salary), 2) AS lop_pct_of_gross
FROM payroll
GROUP BY department
ORDER BY total_lop DESC;

-- 3. Attendance & absenteeism ------------------------------------------------

-- 3a. Absenteeism rate by department (share of working-days marked absent/half-day)
SELECT e.department,
       ROUND(100.0 * SUM(CASE WHEN a.status = 'absent' THEN 1
                               WHEN a.status = 'half-day' THEN 0.5 ELSE 0 END)
             / COUNT(*), 2) AS absenteeism_rate_pct
FROM attendance a
JOIN employees e ON e.employee_id = a.employee_id
GROUP BY e.department
ORDER BY absenteeism_rate_pct DESC;

-- 3b. Absenteeism seasonality — rate by calendar month across all departments
SELECT strftime('%Y-%m', date) AS ym,
       ROUND(100.0 * SUM(CASE WHEN status = 'absent' THEN 1
                               WHEN status = 'half-day' THEN 0.5 ELSE 0 END)
             / COUNT(*), 2) AS absenteeism_rate_pct
FROM attendance
GROUP BY ym
ORDER BY ym;

-- 3c. Employees with the highest personal absenteeism (chronic-absence flag, min 60 recorded days)
SELECT e.employee_id, e.name, e.department,
       COUNT(*) AS days_recorded,
       ROUND(100.0 * SUM(CASE WHEN a.status = 'absent' THEN 1
                               WHEN a.status = 'half-day' THEN 0.5 ELSE 0 END)
             / COUNT(*), 1) AS absenteeism_rate_pct
FROM attendance a
JOIN employees e ON e.employee_id = a.employee_id
GROUP BY e.employee_id
HAVING COUNT(*) >= 60
ORDER BY absenteeism_rate_pct DESC
LIMIT 15;

-- 3d. Friday vs. rest-of-week absence comparison (is the "Friday effect" real?)
SELECT
    CASE WHEN strftime('%w', date) = '5' THEN 'Friday' ELSE 'Other weekday' END AS day_type,
    ROUND(100.0 * SUM(CASE WHEN status = 'absent' THEN 1
                            WHEN status = 'half-day' THEN 0.5 ELSE 0 END) / COUNT(*), 2) AS absence_rate_pct
FROM attendance
WHERE strftime('%w', date) NOT IN ('0')  -- exclude Sunday (not a working day)
GROUP BY day_type;

-- 4. Compensation equity checks ----------------------------------------------

-- 4a. Salary range and spread (min/avg/median-proxy/max) by department & designation
SELECT department, designation,
       COUNT(*)                 AS headcount,
       MIN(basic_salary)        AS min_basic,
       ROUND(AVG(basic_salary), 0) AS avg_basic,
       MAX(basic_salary)        AS max_basic
FROM employees
WHERE status = 'active'
GROUP BY department, designation
ORDER BY department, avg_basic DESC;

-- 4b. Departments where PF + tax load is eating the largest share of gross pay
SELECT department,
       ROUND(SUM(pf) * 100.0 / SUM(gross_salary), 2)               AS pf_pct_of_gross,
       ROUND(SUM(professional_tax) * 100.0 / SUM(gross_salary), 3) AS tax_pct_of_gross
FROM payroll
GROUP BY department
ORDER BY pf_pct_of_gross DESC;

-- 5. Cohort view: new hires in the analysis window vs. tenured staff --------

-- 5a. Average net salary: hired-during-window vs. hired-before-window
SELECT
    CASE WHEN e.date_of_joining >= '2025-08-01' THEN 'Hired in analysis window' ELSE 'Tenured (pre-existing)' END AS cohort,
    COUNT(DISTINCT e.employee_id) AS headcount,
    ROUND(AVG(p.net_salary), 0)   AS avg_monthly_net
FROM employees e
JOIN payroll p ON p.employee_id = e.employee_id AND p.year = 2026 AND p.month = 6
GROUP BY cohort;
