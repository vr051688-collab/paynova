"""
Builds Payroll_Analytics_Workbook.xlsx:
 - Employees, Payroll, Attendance_Monthly: raw data sheets (pivot-table ready)
 - Dashboard: KPI cards + two summary tables built entirely from formulas
   (SUMIFS/COUNTIFS/SUMPRODUCT — no hardcoded results), plus two native
   Excel charts, per the xlsx skill's "formulas, never hardcoded results" rule.
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter

RAW = "/home/claude/payroll-analytics/data/raw"
OUT = "/home/claude/payroll-analytics/excel/Payroll_Analytics_Workbook.xlsx"

employees = pd.read_csv(f"{RAW}/employees.csv")
attendance = pd.read_csv(f"{RAW}/attendance.csv", parse_dates=["date"])
payroll = pd.read_csv(f"{RAW}/payroll.csv")

# Attendance rolled up to employee x month, with department joined in so the
# Dashboard sheet's department-level absenteeism formulas don't need a
# separate lookup table.
att = attendance.merge(employees[["employeeId", "department"]], on="employeeId")
att["year"] = att["date"].dt.year
att["month"] = att["date"].dt.month
att_monthly = (
    att.groupby(["employeeId", "department", "year", "month", "status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
for col in ["present", "absent", "half-day", "leave"]:
    if col not in att_monthly.columns:
        att_monthly[col] = 0
att_monthly["days_recorded"] = att_monthly[["present", "absent", "half-day", "leave"]].sum(axis=1)
att_monthly["absenteeism_rate_pct"] = (
    (att_monthly["absent"] + 0.5 * att_monthly["half-day"]) / att_monthly["days_recorded"] * 100
).round(2)

wb = Workbook()

FONT = "Arial"
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
HEAD_FILL = PatternFill("solid", fgColor="1B2430")
BODY_FONT = Font(name=FONT, size=10)
TITLE_FONT = Font(name=FONT, bold=True, size=18, color="1B2430")
LABEL_FONT = Font(name=FONT, bold=True, size=10, color="5C6B7A")
KPI_FONT = Font(name=FONT, bold=True, size=16, color="1B2430")
THIN = Side(style="thin", color="DDD6C6")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY_FMT = '"₹"#,##0'
PCT_FMT = '0.00"%"'


def write_df_sheet(ws, df, money_cols=()):
    for j, col in enumerate(df.columns, start=1):
        c = ws.cell(row=1, column=j, value=col)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center")
    for i, row in enumerate(df.itertuples(index=False), start=2):
        for j, val in enumerate(row, start=1):
            cell = ws.cell(row=i, column=j, value=val)
            cell.font = BODY_FONT
            if df.columns[j - 1] in money_cols:
                cell.number_format = MONEY_FMT
    for j, col in enumerate(df.columns, start=1):
        width = max(11, min(22, int(df[col].astype(str).str.len().max() if len(df) else 10) + 2))
        ws.column_dimensions[get_column_letter(j)].width = width
    ws.freeze_panes = "A2"


# ---- Employees sheet --------------------------------------------------------
ws_emp = wb.active
ws_emp.title = "Employees"
emp_cols = ["employeeId", "name", "department", "designation", "dateOfJoining", "exitDate",
            "status", "basicSalary", "otherAllowances"]
write_df_sheet(ws_emp, employees[emp_cols], money_cols=["basicSalary", "otherAllowances"])
N_EMP = len(employees)

# ---- Payroll sheet -----------------------------------------------------------
ws_pay = wb.create_sheet("Payroll")
pay_cols = ["employeeId", "department", "year", "month", "workingDays", "presentDays", "absentDays",
            "halfDays", "leaveDays", "basicSalary", "da", "hra", "otherAllowances", "grossSalary",
            "pf", "professionalTax", "lopDeduction", "totalDeductions", "netSalary", "status"]
write_df_sheet(ws_pay, payroll[pay_cols],
               money_cols=["basicSalary", "da", "hra", "otherAllowances", "grossSalary", "pf",
                           "professionalTax", "lopDeduction", "totalDeductions", "netSalary"])
N_PAY = len(payroll)
# column letters we'll reference from Dashboard formulas
PAY_COL = {name: get_column_letter(i + 1) for i, name in enumerate(pay_cols)}

# ---- Attendance_Monthly sheet -------------------------------------------------
ws_att = wb.create_sheet("Attendance_Monthly")
att_cols = ["employeeId", "department", "year", "month", "present", "absent", "half-day", "leave",
            "days_recorded", "absenteeism_rate_pct"]
write_df_sheet(ws_att, att_monthly[att_cols], money_cols=[])
N_ATT = len(att_monthly)
ATT_COL = {name: get_column_letter(i + 1) for i, name in enumerate(att_cols)}

# ---- Dashboard sheet -----------------------------------------------------------
ws = wb.create_sheet("Dashboard", 0)
ws.sheet_view.showGridLines = False
ws["B2"] = "Payroll & Workforce Analytics — FY 2025-26"
ws["B2"].font = TITLE_FONT
ws["B3"] = "All figures below are live formulas against the Employees / Payroll / Attendance_Monthly sheets."
ws["B3"].font = Font(name=FONT, italic=True, size=9, color="5C6B7A")

# --- KPI cards ---
kpis = [
    ("Active Headcount", f'=COUNTIFS(Employees!$G$2:$G${N_EMP+1},"active")', None),
    ("Total Net Payroll (12mo)", f'=SUM(Payroll!${PAY_COL["netSalary"]}$2:${PAY_COL["netSalary"]}${N_PAY+1})', MONEY_FMT),
    ("Avg Absenteeism %",
     f'=SUMPRODUCT(Attendance_Monthly!${ATT_COL["absent"]}$2:${ATT_COL["absent"]}${N_ATT+1}'
     f'+0.5*Attendance_Monthly!${ATT_COL["half-day"]}$2:${ATT_COL["half-day"]}${N_ATT+1})'
     f'/SUM(Attendance_Monthly!${ATT_COL["days_recorded"]}$2:${ATT_COL["days_recorded"]}${N_ATT+1})*100', PCT_FMT),
    ("Total Annual LOP Cost",
     f'=SUM(Payroll!${PAY_COL["lopDeduction"]}$2:${PAY_COL["lopDeduction"]}${N_PAY+1})', MONEY_FMT),
]
kpi_col_start = 2  # column B
for idx, (label, formula, fmt) in enumerate(kpis):
    col = kpi_col_start + idx * 2
    label_cell = ws.cell(row=5, column=col, value=label)
    label_cell.font = LABEL_FONT
    ws.merge_cells(start_row=5, start_column=col, end_row=5, end_column=col + 1)
    val_cell = ws.cell(row=6, column=col, value=formula)
    val_cell.font = KPI_FONT
    if fmt:
        val_cell.number_format = fmt
    ws.merge_cells(start_row=6, start_column=col, end_row=6, end_column=col + 1)

# --- Monthly trend table (row 9 header, 10-21 data) ---
ws["B9"] = "Monthly Payroll Trend"
ws["B9"].font = Font(name=FONT, bold=True, size=12, color="1B2430")
headers = ["Year", "Month", "Label", "Total Gross", "Total Deductions", "Total Net"]
for j, h in enumerate(headers):
    c = ws.cell(row=10, column=2 + j, value=h)
    c.font = HEAD_FONT
    c.fill = HEAD_FILL

months_seq = [(2025, 8, "Aug-25"), (2025, 9, "Sep-25"), (2025, 10, "Oct-25"), (2025, 11, "Nov-25"),
              (2025, 12, "Dec-25"), (2026, 1, "Jan-26"), (2026, 2, "Feb-26"), (2026, 3, "Mar-26"),
              (2026, 4, "Apr-26"), (2026, 5, "May-26"), (2026, 6, "Jun-26"), (2026, 7, "Jul-26")]
first_trend_row = 11
for i, (yr, mo, label) in enumerate(months_seq):
    r = first_trend_row + i
    ws.cell(row=r, column=2, value=yr).font = BODY_FONT
    ws.cell(row=r, column=3, value=mo).font = BODY_FONT
    ws.cell(row=r, column=4, value=label).font = BODY_FONT
    gross_f = (f'=SUMIFS(Payroll!${PAY_COL["grossSalary"]}$2:${PAY_COL["grossSalary"]}${N_PAY+1},'
               f'Payroll!${PAY_COL["year"]}$2:${PAY_COL["year"]}${N_PAY+1},$B{r},'
               f'Payroll!${PAY_COL["month"]}$2:${PAY_COL["month"]}${N_PAY+1},$C{r})')
    ded_f = gross_f.replace(PAY_COL["grossSalary"], PAY_COL["totalDeductions"])
    net_f = gross_f.replace(PAY_COL["grossSalary"], PAY_COL["netSalary"])
    for col_idx, formula in zip([5, 6, 7], [gross_f, ded_f, net_f]):
        cell = ws.cell(row=r, column=col_idx, value=formula)
        cell.number_format = MONEY_FMT
        cell.font = BODY_FONT
last_trend_row = first_trend_row + len(months_seq) - 1

# --- Department table (row 24 header) ---
dept_header_row = 24
ws.cell(row=dept_header_row - 1, column=2, value="Department Summary — June 2026").font = Font(
    name=FONT, bold=True, size=12, color="1B2430"
)
dept_headers = ["Department", "Active Headcount", "Net Cost (Jun-26)", "Absenteeism %"]
for j, h in enumerate(dept_headers):
    c = ws.cell(row=dept_header_row, column=2 + j, value=h)
    c.font = HEAD_FONT
    c.fill = HEAD_FILL

departments = sorted(employees["department"].unique().tolist())
first_dept_row = dept_header_row + 1
for i, dept in enumerate(departments):
    r = first_dept_row + i
    ws.cell(row=r, column=2, value=dept).font = BODY_FONT
    hc_f = f'=COUNTIFS(Employees!${get_column_letter(emp_cols.index("department")+1)}$2:${get_column_letter(emp_cols.index("department")+1)}${N_EMP+1},$B{r},Employees!${get_column_letter(emp_cols.index("status")+1)}$2:${get_column_letter(emp_cols.index("status")+1)}${N_EMP+1},"active")'
    cost_f = (f'=SUMIFS(Payroll!${PAY_COL["netSalary"]}$2:${PAY_COL["netSalary"]}${N_PAY+1},'
              f'Payroll!${PAY_COL["department"]}$2:${PAY_COL["department"]}${N_PAY+1},$B{r},'
              f'Payroll!${PAY_COL["year"]}$2:${PAY_COL["year"]}${N_PAY+1},2026,'
              f'Payroll!${PAY_COL["month"]}$2:${PAY_COL["month"]}${N_PAY+1},6)')
    absent_f = (f'=SUMPRODUCT((Attendance_Monthly!${ATT_COL["department"]}$2:${ATT_COL["department"]}${N_ATT+1}=$B{r})*'
                f'(Attendance_Monthly!${ATT_COL["absent"]}$2:${ATT_COL["absent"]}${N_ATT+1}'
                f'+0.5*Attendance_Monthly!${ATT_COL["half-day"]}$2:${ATT_COL["half-day"]}${N_ATT+1}))'
                f'/SUMPRODUCT((Attendance_Monthly!${ATT_COL["department"]}$2:${ATT_COL["department"]}${N_ATT+1}=$B{r})*'
                f'Attendance_Monthly!${ATT_COL["days_recorded"]}$2:${ATT_COL["days_recorded"]}${N_ATT+1})*100')
    ws.cell(row=r, column=3, value=hc_f).font = BODY_FONT
    cost_cell = ws.cell(row=r, column=4, value=cost_f)
    cost_cell.font = BODY_FONT
    cost_cell.number_format = MONEY_FMT
    pct_cell = ws.cell(row=r, column=5, value=absent_f)
    pct_cell.font = BODY_FONT
    pct_cell.number_format = PCT_FMT
last_dept_row = first_dept_row + len(departments) - 1

for col, width in zip("BCDEFG", [20, 16, 12, 16, 16, 16]):
    ws.column_dimensions[col].width = width

# --- Charts ---
line = LineChart()
line.title = "Net Payroll Trend"
line.y_axis.title = "₹"
line.height, line.width = 8, 16
cats = Reference(ws, min_col=4, min_row=first_trend_row, max_row=last_trend_row)
data = Reference(ws, min_col=7, min_row=10, max_row=last_trend_row)
line.add_data(data, titles_from_data=True)
line.set_categories(cats)
ws.add_chart(line, "I5")

bar = BarChart()
bar.title = "Department Net Cost — Jun 2026"
bar.y_axis.title = "₹"
bar.height, bar.width = 8, 16
cats2 = Reference(ws, min_col=2, min_row=first_dept_row, max_row=last_dept_row)
data2 = Reference(ws, min_col=4, min_row=dept_header_row, max_row=last_dept_row)
bar.add_data(data2, titles_from_data=True)
bar.set_categories(cats2)
ws.add_chart(bar, "I24")

wb.save(OUT)
print("Workbook written:", OUT)
