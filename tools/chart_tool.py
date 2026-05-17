# tools/chart_tool.py
# ---------------------------------------------------------------
# Chart Generation Tool
# Creates matplotlib charts from sales data and saves them
# as images. The agent calls this when user wants to "see" or
# "visualize" or "show a chart" of the data.
# ---------------------------------------------------------------

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import os
from langchain.tools import tool

DATA_PATH = "data/sales_data.csv"
CHART_DIR = "assets"
os.makedirs(CHART_DIR, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["month_period"] = df["date"].dt.to_period("M")
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df


def style_chart(ax, title: str):
    """Apply a clean, professional look to all charts."""
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)
    plt.tight_layout()


@tool
def generate_chart(chart_type: str) -> str:
    """
    Generate a visual chart from sales data and save it as an image.
    Use this tool when the user asks to 'show', 'plot', 'visualize', 
    'chart', or 'graph' any sales data.
    
    Supported chart_type values:
    - 'monthly_revenue'     : line chart of monthly revenue trend
    - 'region_revenue'      : bar chart of revenue by region
    - 'product_revenue'     : bar chart of revenue by product
    - 'rep_performance'     : horizontal bar of sales rep revenue
    - 'category_split'      : pie chart of revenue by category
    - 'profit_by_product'   : bar chart of profit by product
    - 'quarterly_revenue'   : bar chart of quarterly revenue
    
    Returns the file path of the saved chart image.
    """
    df = load_data()
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#4C6EF5", "#F76707", "#2F9E44", "#E03131", "#7950F2", "#1098AD"]

    ct = chart_type.lower().strip()

    if ct == "monthly_revenue":
        data = df.groupby("month_period")["revenue"].sum().sort_index()
        ax.plot([str(m) for m in data.index], data.values / 1000,
                marker="o", color=colors[0], linewidth=2, markersize=6)
        ax.fill_between(range(len(data)), data.values / 1000, alpha=0.1, color=colors[0])
        ax.set_xticklabels([str(m) for m in data.index], rotation=45, ha="right")
        ax.set_ylabel("Revenue (₹ thousands)")
        style_chart(ax, "Monthly Revenue Trend (2024)")
        fname = "monthly_revenue.png"

    elif ct == "region_revenue":
        data = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
        bars = ax.bar(data.index, data.values / 1000, color=colors[:len(data)], edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, data.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    f"₹{val/1000:.0f}K", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_ylabel("Revenue (₹ thousands)")
        style_chart(ax, "Revenue by Region")
        fname = "region_revenue.png"

    elif ct == "product_revenue":
        data = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
        bars = ax.bar(data.index, data.values / 1000, color=colors[:len(data)], edgecolor="white", linewidth=0.5)
        ax.set_xticklabels(data.index, rotation=20, ha="right")
        ax.set_ylabel("Revenue (₹ thousands)")
        style_chart(ax, "Revenue by Product")
        fname = "product_revenue.png"

    elif ct == "rep_performance":
        data = df.groupby("sales_rep")["revenue"].sum().sort_values()
        bars = ax.barh(data.index, data.values / 1000, color=colors[4], edgecolor="white")
        for bar, val in zip(bars, data.values):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                    f"₹{val/1000:.0f}K", va="center", fontsize=9, fontweight="bold")
        ax.set_xlabel("Revenue (₹ thousands)")
        style_chart(ax, "Sales Rep Performance")
        fname = "rep_performance.png"

    elif ct == "category_split":
        data = df.groupby("category")["revenue"].sum()
        wedges, texts, autotexts = ax.pie(
            data.values, labels=data.index, autopct="%1.1f%%",
            colors=colors[:len(data)], startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2}
        )
        for at in autotexts:
            at.set_fontsize(11)
            at.set_fontweight("bold")
        style_chart(ax, "Revenue Split by Category")
        fname = "category_split.png"

    elif ct == "profit_by_product":
        data = df.groupby("product")["profit"].sum().sort_values(ascending=False)
        bars = ax.bar(data.index, data.values / 1000, color=colors[2], edgecolor="white", linewidth=0.5)
        ax.set_xticklabels(data.index, rotation=20, ha="right")
        ax.set_ylabel("Profit (₹ thousands)")
        style_chart(ax, "Profit by Product")
        fname = "profit_by_product.png"

    elif ct == "quarterly_revenue":
        data = df.groupby("quarter")["revenue"].sum()
        bars = ax.bar(data.index, data.values / 1000, color=colors[:len(data)], edgecolor="white")
        for bar, val in zip(bars, data.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    f"₹{val/1000:.0f}K", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_ylabel("Revenue (₹ thousands)")
        style_chart(ax, "Quarterly Revenue (2024)")
        fname = "quarterly_revenue.png"

    else:
        plt.close()
        return (f"Unknown chart type: '{chart_type}'. "
                f"Supported: monthly_revenue, region_revenue, product_revenue, "
                f"rep_performance, category_split, profit_by_product, quarterly_revenue")

    path = os.path.join(CHART_DIR, fname)
    plt.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close()
    return path
