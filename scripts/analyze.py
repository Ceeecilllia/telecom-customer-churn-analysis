"""Generate reproducible analysis tables and portfolio-ready figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "telecom_customers_clean.csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

STATUS_COLORS = {"Stayed": "#2A9D8F", "Churned": "#E76F51", "Joined": "#457B9D"}
RISK_COLORS = {"Low": "#82C09A", "Medium": "#F4A261", "High": "#D1495B"}


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run python scripts/preprocess.py before this script.")
    return pd.read_csv(DATA_PATH)


def segment_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    summary = (
        df.groupby(column, dropna=False)
        .agg(
            customers=("customer_id", "size"),
            churned_customers=("churn_flag", "sum"),
            churn_rate=("churn_flag", "mean"),
            avg_monthly_charge=("monthly_charge_valid", "mean"),
            historical_revenue=("total_revenue", "sum"),
        )
        .reset_index()
    )
    summary["churn_rate_pct"] = (summary["churn_rate"] * 100).round(2)
    summary["avg_monthly_charge"] = summary["avg_monthly_charge"].round(2)
    summary["historical_revenue"] = summary["historical_revenue"].round(2)
    return summary.sort_values("churn_rate", ascending=False)


def save_segment_tables(df: pd.DataFrame) -> None:
    columns = [
        "contract",
        "internet_type_clean",
        "payment_method",
        "paperless_billing",
        "offer_clean",
        "online_security",
        "online_backup",
        "device_protection_plan",
        "premium_tech_support",
    ]
    for column in columns:
        segment_summary(df, column).to_csv(TABLE_DIR / f"churn_by_{column}.csv", index=False)

    reasons = (
        df.loc[df["churn_flag"].eq(1), ["churn_category", "churn_reason"]]
        .value_counts()
        .rename("churned_customers")
        .reset_index()
    )
    reasons["share_of_churn_pct"] = (reasons["churned_customers"] / reasons["churned_customers"].sum() * 100).round(2)
    reasons.to_csv(TABLE_DIR / "churn_reasons.csv", index=False)

    priority = (
        df.groupby("risk_priority", observed=True)
        .agg(
            customers=("customer_id", "size"),
            churned_customers=("churn_flag", "sum"),
            observed_churn_rate=("churn_flag", "mean"),
            monthly_revenue_exposure_raw=(
                "monthly_charge_raw",
                lambda values: values[df.loc[values.index, "churn_flag"].eq(1)].sum(),
            ),
        )
        .reindex(["Low", "Medium", "High"])
        .reset_index()
    )
    priority["observed_churn_rate_pct"] = (priority["observed_churn_rate"] * 100).round(2)
    priority["monthly_revenue_exposure_raw"] = priority["monthly_revenue_exposure_raw"].round(2)
    priority.to_csv(TABLE_DIR / "retention_priority_summary.csv", index=False)

    actionable = df.loc[
        df["customer_status"].isin(["Stayed", "Joined"]) & df["risk_priority"].eq("High"),
        [
            "customer_id",
            "customer_status",
            "tenure_in_months",
            "contract",
            "internet_type_clean",
            "monthly_charge_valid",
            "total_revenue",
            "descriptive_risk_score",
            "risk_priority",
        ],
    ].sort_values(["monthly_charge_valid", "tenure_in_months"], ascending=[False, True])
    actionable.to_csv(TABLE_DIR / "high_priority_active_customers.csv", index=False)


def style_axes(ax: plt.Axes, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E7E7E7", linewidth=0.8)


def plot_contract_churn(df: pd.DataFrame) -> None:
    order = ["Month-to-Month", "One Year", "Two Year"]
    summary = segment_summary(df, "contract").set_index("contract").reindex(order).reset_index()
    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.bar(summary["contract"], summary["churn_rate_pct"], color=["#D1495B", "#F4A261", "#82C09A"])
    ax.bar_label(bars, fmt="%.2f%%", padding=4, fontweight="bold")
    ax.set_ylim(0, 52)
    style_axes(ax, "Churn declines sharply with longer contracts", ylabel="Churn rate (%)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "contract_churn_rate.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_contract_internet_heatmap(df: pd.DataFrame) -> None:
    pivot = df.pivot_table(
        index="contract",
        columns="internet_type_clean",
        values="churn_flag",
        aggfunc="mean",
    ) * 100
    pivot = pivot.reindex(["Month-to-Month", "One Year", "Two Year"])
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=1, cbar_kws={"label": "Churn rate (%)"}, ax=ax)
    ax.set_title("Month-to-month fiber customers show the highest churn", loc="left", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Internet type")
    ax.set_ylabel("Contract")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "contract_internet_heatmap.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_tenure_charge(df: pd.DataFrame) -> None:
    plot_df = df.dropna(subset=["monthly_charge_valid"])
    fig, ax = plt.subplots(figsize=(9.5, 5.7))
    for status in ["Stayed", "Joined", "Churned"]:
        part = plot_df[plot_df["customer_status"].eq(status)]
        ax.scatter(
            part["tenure_in_months"],
            part["monthly_charge_valid"],
            s=14,
            alpha=0.38,
            color=STATUS_COLORS[status],
            label=f"{status} ({len(part):,})",
            edgecolors="none",
        )
    ax.axvline(12, color="#555555", linestyle="--", linewidth=1)
    ax.axhline(70, color="#555555", linestyle="--", linewidth=1)
    ax.text(1.5, 113, "Short tenure + high charge", fontsize=9, color="#333333")
    style_axes(ax, "Short-tenure, high-charge customers warrant early attention", "Tenure (months)", "Validated monthly charge ($)")
    ax.legend(frameon=False, ncol=3, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "tenure_monthly_charge.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_risk_priority(df: pd.DataFrame) -> None:
    summary = (
        df.groupby("risk_priority", observed=True)["churn_flag"]
        .agg(customers="size", churn_rate="mean")
        .reindex(["Low", "Medium", "High"])
        .reset_index()
    )
    summary["churn_rate_pct"] = summary["churn_rate"] * 100
    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.bar(
        summary["risk_priority"],
        summary["churn_rate_pct"],
        color=[RISK_COLORS[x] for x in summary["risk_priority"]],
    )
    labels = [f"{rate:.1f}%\n(n={count:,})" for rate, count in zip(summary["churn_rate_pct"], summary["customers"])]
    ax.bar_label(bars, labels=labels, padding=4, fontweight="bold")
    ax.set_ylim(0, 65)
    style_axes(ax, "Transparent rules separate materially different risk groups", ylabel="Observed churn rate (%)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "risk_priority_churn.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    sns.set_theme(style="whitegrid", font_scale=1.0)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    save_segment_tables(df)
    plot_contract_churn(df)
    plot_contract_internet_heatmap(df)
    plot_tenure_charge(df)
    plot_risk_priority(df)
    print(f"Generated analysis outputs for {len(df):,} customers.")


if __name__ == "__main__":
    main()
