# SQL Analysis Results

Generated from `analysis_queries.sql` against `payroll_analytics.db`.

## 1a_headcount_by_department

| department   |   headcount |   pct_of_workforce |
|:-------------|------------:|-------------------:|
| Engineering  |          46 |               25.8 |
| Sales        |          31 |               17.4 |
| Finance      |          26 |               14.6 |
| Support      |          23 |               12.9 |
| Operations   |          19 |               10.7 |
| Marketing    |          18 |               10.1 |
| HR           |          15 |                8.4 |


## 1b_headcount_trend_by_month

| ym      |   headcount_at_month_end |
|:--------|-------------------------:|
| 2025-08 |                      165 |
| 2025-09 |                      169 |
| 2025-10 |                      170 |
| 2025-11 |                      173 |
| 2025-12 |                      176 |
| 2026-01 |                      176 |
| 2026-02 |                      177 |
| 2026-03 |                      177 |
| 2026-04 |                      179 |
| 2026-05 |                      179 |
| 2026-06 |                      180 |
| 2026-07 |                      178 |


## 1c_exits_by_month

| exit_month   |   exits |
|:-------------|--------:|
| 2025-09      |       2 |
| 2025-12      |       1 |
| 2026-02      |       1 |
| 2026-05      |       1 |
| 2026-06      |       2 |


## 1d_tenure_distribution

| tenure_bucket   |   employees |
|:----------------|------------:|
| 0-6 months      |           6 |
| 6-12 months     |          18 |
| 1-2 years       |          71 |
| 2-4 years       |          82 |
| 4+ years        |           1 |


## 2a_monthly_payroll_cost_trend

|   year |   month |   total_gross |   total_deductions |   total_net |   payslips |
|-------:|--------:|--------------:|-------------------:|------------:|-----------:|
|   2025 |       8 |   9.69322e+06 |        1.40324e+06 | 8.28998e+06 |        165 |
|   2025 |       9 |   9.91882e+06 |        1.49158e+06 | 8.42724e+06 |        169 |
|   2025 |      10 |   9.99019e+06 |        1.60197e+06 | 8.38822e+06 |        170 |
|   2025 |      11 |   1.01995e+07 |        1.59411e+06 | 8.60537e+06 |        173 |
|   2025 |      12 |   1.03951e+07 |        1.55047e+06 | 8.8446e+06  |        177 |
|   2026 |       1 |   1.03428e+07 |        1.48148e+06 | 8.86135e+06 |        176 |
|   2026 |       2 |   1.0391e+07  |        1.50443e+06 | 8.88659e+06 |        177 |
|   2026 |       3 |   1.04148e+07 |        1.51415e+06 | 8.90066e+06 |        177 |
|   2026 |       4 |   1.13162e+07 |        1.68472e+06 | 9.63144e+06 |        179 |
|   2026 |       5 |   1.13641e+07 |        1.7305e+06  | 9.63364e+06 |        180 |
|   2026 |       6 |   1.13363e+07 |        1.75868e+06 | 9.57762e+06 |        180 |
|   2026 |       7 |   1.12152e+07 |        1.54866e+06 | 9.66658e+06 |        178 |


## 2b_department_cost_latest_month

| department   |   headcount |   total_net_cost |   avg_net_salary |
|:-------------|------------:|-----------------:|-----------------:|
| Engineering  |          47 |      3.28089e+06 |            69806 |
| Sales        |          31 |      1.48897e+06 |            48031 |
| Finance      |          27 |      1.4871e+06  |            55078 |
| Support      |          23 | 879354           |            38233 |
| Operations   |          19 | 860464           |            45288 |
| Marketing    |          18 | 854230           |            47457 |
| HR           |          15 | 726612           |            48441 |


## 2c_mom_payroll_growth

|   year |   month |   total_net |   mom_growth_pct |
|-------:|--------:|------------:|-----------------:|
|   2025 |       8 | 8.28998e+06 |           nan    |
|   2025 |       9 | 8.42724e+06 |             1.66 |
|   2025 |      10 | 8.38822e+06 |            -0.46 |
|   2025 |      11 | 8.60537e+06 |             2.59 |
|   2025 |      12 | 8.8446e+06  |             2.78 |
|   2026 |       1 | 8.86135e+06 |             0.19 |
|   2026 |       2 | 8.88659e+06 |             0.28 |
|   2026 |       3 | 8.90066e+06 |             0.16 |
|   2026 |       4 | 9.63144e+06 |             8.21 |
|   2026 |       5 | 9.63364e+06 |             0.02 |
|   2026 |       6 | 9.57762e+06 |            -0.58 |
|   2026 |       7 | 9.66658e+06 |             0.93 |


## 2d_top10_highest_cost_employees

| employee_id   | name            | department   | designation              |   total_net_paid_ytd |
|:--------------|:----------------|:-------------|:-------------------------|---------------------:|
| EMP0158       | Divya Kumar     | Engineering  | DevOps Engineer          |          1.13187e+06 |
| EMP0025       | Rahul Reddy     | Engineering  | Senior Software Engineer |          1.11662e+06 |
| EMP0135       | Naveen Bose     | Engineering  | QA Engineer              |          1.10099e+06 |
| EMP0031       | Sneha Iyer      | Engineering  | QA Engineer              |          1.06066e+06 |
| EMP0016       | Sneha Verma     | Engineering  | QA Engineer              |          1.02686e+06 |
| EMP0034       | Rohan Gupta     | Engineering  | DevOps Engineer          |          1.02099e+06 |
| EMP0142       | Prakash Shetty  | Engineering  | Software Engineer        |          1.00977e+06 |
| EMP0139       | Swathi Pillai   | Engineering  | DevOps Engineer          |     953622           |
| EMP0061       | Sunita Kulkarni | Engineering  | Senior Software Engineer |     951393           |
| EMP0185       | Ananya Nair     | Engineering  | DevOps Engineer          |     935657           |


## 2e_lop_impact_by_department

| department   |        total_lop |   lop_pct_of_gross |
|:-------------|-----------------:|-------------------:|
| Engineering  |      1.44077e+06 |               3.3  |
| Sales        |      1.00202e+06 |               5.06 |
| Finance      | 553750           |               2.84 |
| Support      | 546357           |               4.67 |
| Operations   | 447344           |               3.82 |
| Marketing    | 408375           |               3.79 |
| HR           | 303516           |               3.24 |


## 3a_absenteeism_by_department

| department   |   absenteeism_rate_pct |
|:-------------|-----------------------:|
| Sales        |                   5.27 |
| Support      |                   4.87 |
| Operations   |                   4.04 |
| Marketing    |                   4.01 |
| HR           |                   3.42 |
| Engineering  |                   3.34 |
| Finance      |                   2.99 |


## 3b_absenteeism_seasonality

| ym      |   absenteeism_rate_pct |
|:--------|-----------------------:|
| 2025-08 |                   3.34 |
| 2025-09 |                   4.02 |
| 2025-10 |                   5.02 |
| 2025-11 |                   4.42 |
| 2025-12 |                   3.97 |
| 2026-01 |                   3.2  |
| 2026-02 |                   3.36 |
| 2026-03 |                   3.46 |
| 2026-04 |                   3.66 |
| 2026-05 |                   4.16 |
| 2026-06 |                   4.42 |
| 2026-07 |                   4.71 |


## 3c_chronic_absence_flag

| employee_id   | name            | department   |   days_recorded |   absenteeism_rate_pct |
|:--------------|:----------------|:-------------|----------------:|-----------------------:|
| EMP0083       | Girish Menon    | Sales        |             302 |                    8.8 |
| EMP0140       | Suresh Reddy    | Sales        |             302 |                    8.3 |
| EMP0114       | Ashok Kulkarni  | Marketing    |              74 |                    8.1 |
| EMP0003       | Siddharth Joshi | Sales        |             302 |                    7.9 |
| EMP0056       | Divya Verma     | Operations   |             302 |                    7.6 |
| EMP0145       | Deepika Gupta   | Sales        |             302 |                    7.5 |
| EMP0065       | Vivek Patil     | Support      |             302 |                    7.1 |
| EMP0096       | Nisha Nair      | Support      |             302 |                    7.1 |
| EMP0020       | Nisha Iyer      | Support      |             302 |                    6.8 |
| EMP0031       | Sneha Iyer      | Engineering  |             302 |                    6.8 |
| EMP0094       | Rahul Bhat      | Support      |             302 |                    6.8 |
| EMP0185       | Ananya Nair     | Engineering  |             302 |                    6.6 |
| EMP0081       | Bhavana Kumar   | Sales        |             302 |                    6.5 |
| EMP0115       | Chitra Reddy    | Support      |             170 |                    6.5 |
| EMP0066       | Swathi Bhat     | Sales        |             302 |                    6.3 |


## 3d_friday_effect

| day_type      |   absence_rate_pct |
|:--------------|-------------------:|
| Friday        |               4.09 |
| Other weekday |               3.93 |


## 4a_salary_bands

| department   | designation                    |   headcount |   min_basic |   avg_basic |   max_basic |
|:-------------|:-------------------------------|------------:|------------:|------------:|------------:|
| Engineering  | QA Engineer                    |           9 |       39000 |       66111 |       85000 |
| Engineering  | Senior Software Engineer       |           8 |       47000 |       61000 |       83500 |
| Engineering  | DevOps Engineer                |          14 |       41000 |       60000 |       88000 |
| Engineering  | Software Engineer              |           7 |       49500 |       59929 |       77000 |
| Engineering  | Engineering Manager            |           8 |       40500 |       57813 |       70000 |
| Finance      | Finance Manager                |           7 |       41500 |       51714 |       63000 |
| Finance      | Accounts Executive             |           5 |       42000 |       49700 |       57500 |
| Finance      | Financial Analyst              |          14 |       36000 |       48000 |       67000 |
| HR           | HR Executive                   |           3 |       36500 |       45333 |       53000 |
| HR           | Talent Acquisition Specialist  |           4 |       38000 |       44625 |       51000 |
| HR           | HR Manager                     |           8 |       32500 |       40313 |       51000 |
| Marketing    | Marketing Manager              |           5 |       36000 |       44600 |       51500 |
| Marketing    | SEO Specialist                 |           4 |       33500 |       41750 |       48000 |
| Marketing    | Marketing Associate            |           4 |       29500 |       40625 |       49500 |
| Marketing    | Content Strategist             |           5 |       30500 |       40200 |       53500 |
| Operations   | Operations Analyst             |           5 |       31000 |       45100 |       51000 |
| Operations   | Operations Manager             |           7 |       29000 |       40286 |       52500 |
| Operations   | Operations Executive           |           7 |       29000 |       37929 |       44000 |
| Sales        | Senior Sales Executive         |           8 |       35500 |       48125 |       61000 |
| Sales        | Sales Executive                |          10 |       31500 |       45100 |       58500 |
| Sales        | Sales Manager                  |           3 |       38500 |       41000 |       43500 |
| Sales        | Business Development Associate |          10 |       29000 |       40500 |       55500 |
| Support      | Senior Support Associate       |           6 |       31500 |       35000 |       38000 |
| Support      | Support Associate              |          11 |       23500 |       34682 |       46500 |
| Support      | Support Team Lead              |           6 |       23000 |       30750 |       39500 |


## 4b_statutory_load_by_department

| department   |   pf_pct_of_gross |   tax_pct_of_gross |
|:-------------|------------------:|-------------------:|
| Engineering  |             10.9  |              0.256 |
| Finance      |             10.88 |              0.324 |
| Sales        |             10.88 |              0.359 |
| Operations   |             10.86 |              0.387 |
| Marketing    |             10.77 |              0.372 |
| HR           |             10.76 |              0.37  |
| Support      |             10.75 |              0.463 |


## 5a_new_hire_vs_tenured_pay

| cohort                   |   headcount |   avg_monthly_net |
|:-------------------------|------------:|------------------:|
| Hired in analysis window |          21 |             46812 |
| Tenured (pre-existing)   |         159 |             54054 |

