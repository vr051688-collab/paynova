import json
import pandas as pd

with open("/home/claude/payroll-analytics/python_analysis/summary_stats.json") as f:
    s = json.load(f)

payroll = pd.read_csv("/home/claude/payroll-analytics/data/raw/payroll.csv")
monthly = payroll.groupby(["year", "month"], as_index=False).agg(
    total_net=("netSalary", "sum"), total_gross=("grossSalary", "sum")
).sort_values(["year", "month"])
monthly["label"] = monthly.apply(lambda r: f"{int(r.year)}-{int(r.month):02d}", axis=1)

data = {
    "kpis": {
        "active_headcount": s["active_headcount"],
        "attrition_rate_pct": s["attrition_rate_pct"],
        "current_monthly_net_payroll_inr": s["current_monthly_net_payroll_inr"],
        "trailing_12m_net_payroll_inr": s["trailing_12m_net_payroll_inr"],
        "payroll_cost_growth_pct": s["payroll_cost_growth_aug_to_jul_pct"],
        "avg_tenure_months": s["avg_tenure_months"],
        "annual_lop_cost_inr": s["annual_lop_cost_inr"],
        "forecast_r2": s["payroll_forecast"]["r_squared"],
    },
    "payroll_trend": {
        "labels": monthly["label"].tolist(),
        "net": [round(v) for v in monthly["total_net"].tolist()],
        "gross": [round(v) for v in monthly["total_gross"].tolist()],
        "forecast_labels": [row["month"] for row in s["payroll_forecast"]["next_3_months"]],
        "forecast_net": [round(row["forecast_net_payroll_inr"]) for row in s["payroll_forecast"]["next_3_months"]],
    },
    "headcount_by_department": s["headcount_by_department"],
    "department_cost_latest": s["department_cost_latest_month"]["data"],
    "department_cost_month_label": s["department_cost_latest_month"]["month"],
    "absenteeism_trend": s["absenteeism_trend_pct"],
    "absenteeism_by_department": s["absenteeism_by_department_pct"],
    "lop_by_department": s["lop_by_department"],
    "tenure_distribution": s["tenure_distribution"],
    "top_10_earners": s["top_10_earners_ytd"],
    "pay_concentration_top10_pct": s["pay_concentration_top10_pct_of_total"],
    "correlation_absence_lop": s["absenteeism_vs_lop_cost_correlation"],
}

with open("/home/claude/payroll-analytics/bi_dashboards/dashboard_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("dashboard_data.json written")
print(json.dumps(data["kpis"], indent=2))
