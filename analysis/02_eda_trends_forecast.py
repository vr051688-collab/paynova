"""
Core analysis layer: pandas/numpy EDA + trend analysis, and a scikit-learn
linear regression forecast for payroll cost and headcount. Produces:
 - PNG charts (python_analysis/charts/*.png) reused by the HTML dashboard
   and the Word report
 - python_analysis/summary_stats.json — every headline number, in one place,
   so the dashboard/report/README never hardcode a number that could drift
   out of sync with the data
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

RAW = "/home/claude/payroll-analytics/data/raw"
CHARTS = "/home/claude/payroll-analytics/python_analysis/charts"

# ---- house style for every chart ------------------------------------------
INK = "#1B2430"
GOLD = "#B08D57"
SLATE = "#5C6B7A"
PALETTE = ["#1B2430", "#B08D57", "#5C6B7A", "#8C4B3F", "#6B8F71", "#3E5C76", "#C9A87C"]
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": SLATE,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": SLATE,
    "ytick.color": SLATE,
    "axes.grid": True,
    "grid.color": "#E4E0D8",
    "grid.linewidth": 0.7,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

employees = pd.read_csv(f"{RAW}/employees.csv", parse_dates=["dateOfJoining"])
employees["exitDate"] = pd.to_datetime(employees["exitDate"], errors="coerce")
attendance = pd.read_csv(f"{RAW}/attendance.csv", parse_dates=["date"])
payroll = pd.read_csv(f"{RAW}/payroll.csv")
payroll["period"] = pd.to_datetime(payroll["year"].astype(str) + "-" + payroll["month"].astype(str) + "-01")

summary = {}

# ---------------------------------------------------------------------------
# 1. Workforce composition
# ---------------------------------------------------------------------------
active = employees[employees.status == "active"]
summary["total_employees_ever"] = int(len(employees))
summary["active_headcount"] = int(len(active))
summary["inactive_headcount"] = int(len(employees) - len(active))
summary["attrition_rate_pct"] = round(100 * summary["inactive_headcount"] / summary["total_employees_ever"], 2)

dept_headcount = active.groupby("department").size().sort_values(ascending=False)
summary["headcount_by_department"] = dept_headcount.to_dict()

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.barh(dept_headcount.index[::-1], dept_headcount.values[::-1], color=PALETTE[0])
ax.set_xlabel("Active employees")
ax.set_title("Headcount by department", fontsize=13, fontweight="bold", loc="left")
for i, v in enumerate(dept_headcount.values[::-1]):
    ax.text(v + 0.5, i, str(v), va="center", fontsize=9, color=INK)
plt.tight_layout()
plt.savefig(f"{CHARTS}/headcount_by_department.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 2. Payroll cost trend + forecast (scikit-learn linear regression)
# ---------------------------------------------------------------------------
monthly = payroll.groupby("period", as_index=False).agg(
    total_gross=("grossSalary", "sum"), total_net=("netSalary", "sum"), payslips=("employeeId", "count")
).sort_values("period")
monthly["t"] = np.arange(len(monthly))

X = monthly[["t"]].values
y = monthly["total_net"].values
model = LinearRegression().fit(X, y)
r2 = r2_score(y, model.predict(X))
mae = mean_absolute_error(y, model.predict(X))

future_t = np.arange(len(monthly), len(monthly) + 3).reshape(-1, 1)
forecast = model.predict(future_t)
future_periods = pd.date_range(monthly["period"].max() + pd.DateOffset(months=1), periods=3, freq="MS")

summary["payroll_forecast"] = {
    "method": "Linear regression on 12 months of net payroll cost (scikit-learn)",
    "r_squared": round(float(r2), 4),
    "mae_inr": round(float(mae), 0),
    "monthly_growth_inr": round(float(model.coef_[0]), 0),
    "next_3_months": [
        {"month": p.strftime("%Y-%m"), "forecast_net_payroll_inr": round(float(f), 0)}
        for p, f in zip(future_periods, forecast)
    ],
}
summary["current_monthly_net_payroll_inr"] = round(float(monthly["total_net"].iloc[-1]), 0)
summary["trailing_12m_net_payroll_inr"] = round(float(monthly["total_net"].sum()), 0)
summary["payroll_cost_growth_aug_to_jul_pct"] = round(
    100 * (monthly["total_net"].iloc[-1] / monthly["total_net"].iloc[0] - 1), 2
)

fig, ax = plt.subplots(figsize=(8.5, 4.5))
ax.plot(monthly["period"], monthly["total_net"] / 1e5, marker="o", color=INK, linewidth=2, label="Actual net payroll")
all_periods = list(monthly["period"]) + list(future_periods)
all_values = list(monthly["total_net"] / 1e5) + list(forecast / 1e5)
ax.plot(future_periods, forecast / 1e5, marker="o", linestyle="--", color=GOLD, linewidth=2, label="Forecast (next 3 months)")
ax.axvline(monthly["period"].max(), color=SLATE, linestyle=":", linewidth=1)
ax.set_ylabel("Net payroll cost (\u20b9 lakh)")
ax.set_title("Monthly net payroll cost — trend and 3-month forecast", fontsize=13, fontweight="bold", loc="left")
ax.legend(frameon=False)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %y"))
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{CHARTS}/payroll_trend_forecast.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 3. Department cost breakdown (latest paid month)
# ---------------------------------------------------------------------------
latest_paid = payroll[payroll.status == "paid"]["period"].max()
dept_cost = (
    payroll[payroll.period == latest_paid]
    .groupby("department", as_index=False)
    .agg(total_net=("netSalary", "sum"), headcount=("employeeId", "count"))
    .sort_values("total_net", ascending=False)
)
summary["department_cost_latest_month"] = {
    "month": latest_paid.strftime("%Y-%m"),
    "data": dept_cost.set_index("department")["total_net"].round(0).to_dict(),
}

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.bar(dept_cost["department"], dept_cost["total_net"] / 1e5, color=PALETTE[:len(dept_cost)])
ax.set_ylabel("Net payroll cost (\u20b9 lakh)")
ax.set_title(f"Department payroll cost — {latest_paid.strftime('%B %Y')}", fontsize=13, fontweight="bold", loc="left")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig(f"{CHARTS}/department_cost.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 4. Absenteeism trend + department comparison
# ---------------------------------------------------------------------------
attendance["ym"] = attendance["date"].dt.to_period("M").astype(str)
absence_weight = attendance["status"].map({"absent": 1.0, "half-day": 0.5, "leave": 0.0, "present": 0.0})
attendance["absence_weight"] = absence_weight
monthly_absence = attendance.groupby("ym")["absence_weight"].mean().mul(100).round(2)
summary["absenteeism_trend_pct"] = monthly_absence.to_dict()
summary["peak_absenteeism_month"] = monthly_absence.idxmax()
summary["lowest_absenteeism_month"] = monthly_absence.idxmin()

att_with_dept = attendance.merge(employees[["employeeId", "department"]], on="employeeId")
dept_absence = att_with_dept.groupby("department")["absence_weight"].mean().mul(100).round(2).sort_values(ascending=False)
summary["absenteeism_by_department_pct"] = dept_absence.to_dict()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.3))
ax1.plot(monthly_absence.index, monthly_absence.values, marker="o", color="#8C4B3F", linewidth=2)
ax1.set_title("Absenteeism rate by month", fontsize=12, fontweight="bold", loc="left")
ax1.set_ylabel("% of working days")
plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

ax2.barh(dept_absence.index[::-1], dept_absence.values[::-1], color="#8C4B3F")
ax2.set_title("Absenteeism rate by department", fontsize=12, fontweight="bold", loc="left")
ax2.set_xlabel("% of working days")
plt.tight_layout()
plt.savefig(f"{CHARTS}/absenteeism.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 5. Tenure distribution
# ---------------------------------------------------------------------------
TODAY = pd.Timestamp("2026-07-18")
active = active.copy()
active["tenure_months"] = (TODAY - active["dateOfJoining"]).dt.days / 30.44
bins = [0, 6, 12, 24, 48, 999]
labels = ["0-6 mo", "6-12 mo", "1-2 yr", "2-4 yr", "4+ yr"]
active["tenure_bucket"] = pd.cut(active["tenure_months"], bins=bins, labels=labels)
tenure_dist = active["tenure_bucket"].value_counts().reindex(labels)
summary["tenure_distribution"] = tenure_dist.to_dict()
summary["avg_tenure_months"] = round(float(active["tenure_months"].mean()), 1)

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.bar(tenure_dist.index.astype(str), tenure_dist.values, color=PALETTE[1])
ax.set_ylabel("Active employees")
ax.set_title("Tenure distribution (active employees)", fontsize=13, fontweight="bold", loc="left")
plt.tight_layout()
plt.savefig(f"{CHARTS}/tenure_distribution.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 6. LOP (loss-of-pay) cost vs absenteeism — is absenteeism actually costing us?
# ---------------------------------------------------------------------------
dept_lop = payroll.groupby("department", as_index=False).agg(
    total_lop=("lopDeduction", "sum"), total_gross=("grossSalary", "sum")
)
dept_lop["lop_pct_of_gross"] = (dept_lop["total_lop"] / dept_lop["total_gross"] * 100).round(2)
summary["annual_lop_cost_inr"] = round(float(payroll["lopDeduction"].sum()), 0)
summary["lop_by_department"] = dept_lop.set_index("department")["total_lop"].round(0).to_dict()

corr = np.corrcoef(dept_absence.reindex(dept_lop["department"]).values, dept_lop["lop_pct_of_gross"].values)[0, 1]
summary["absenteeism_vs_lop_cost_correlation"] = round(float(corr), 3)

# ---------------------------------------------------------------------------
# 7. Top earners & pay concentration
# ---------------------------------------------------------------------------
ytd_pay = payroll.groupby("employeeId")["netSalary"].sum().sort_values(ascending=False)
top10 = ytd_pay.head(10).reset_index().merge(employees[["employeeId", "name", "department"]], on="employeeId")
summary["top_10_earners_ytd"] = [
    {"name": r["name"], "department": r["department"], "net_paid_ytd_inr": round(r["netSalary"], 0)}
    for _, r in top10.iterrows()
]
summary["pay_concentration_top10_pct_of_total"] = round(100 * ytd_pay.head(10).sum() / ytd_pay.sum(), 2)

fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.barh(top10["name"][::-1], top10["netSalary"][::-1] / 1e5, color=GOLD)
ax.set_xlabel("Net paid, YTD (\u20b9 lakh)")
ax.set_title("Top 10 earners — YTD net pay", fontsize=13, fontweight="bold", loc="left")
plt.tight_layout()
plt.savefig(f"{CHARTS}/top10_earners.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Save summary
# ---------------------------------------------------------------------------
with open("/home/claude/payroll-analytics/python_analysis/summary_stats.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("Charts saved to", CHARTS)
print("Summary stats saved to python_analysis/summary_stats.json")
print(f"\nForecast R^2 = {r2:.3f}, MAE = Rs {mae:,.0f}")
print("Next 3 months forecast:")
for row in summary["payroll_forecast"]["next_3_months"]:
    print(" ", row)
