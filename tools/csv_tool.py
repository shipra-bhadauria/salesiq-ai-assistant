# tools/csv_tool.py
# ---------------------------------------------------------------
# CSV Analysis Tool
# This tool lets the agent read and analyze the sales CSV file
# using pandas. The agent calls this when user asks data questions.
# ---------------------------------------------------------------

import pandas as pd
from langchain.tools import tool

DATA_PATH = "data/sales_data.csv"


def load_data() -> pd.DataFrame:
    """Load and preprocess the sales CSV."""
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month_name()
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df


@tool
def analyze_sales_data(query: str) -> str:
    """
    Analyze sales data from the CSV file.
    Use this tool when the user asks about revenue, profit, 
    sales reps, products, regions, trends, top performers, 
    comparisons, or any numerical/statistical question about sales.
    
    Input: a plain English description of what to compute.
    Output: a clear text answer with numbers.
    """
    df = load_data()

    q = query.lower()

    # --- Total revenue ---
    if "total revenue" in q or "overall revenue" in q:
        total = df["revenue"].sum()
        return f"Total revenue across all orders: ₹{total:,.0f}"

    # --- Total profit ---
    if "total profit" in q or "overall profit" in q:
        total = df["profit"].sum()
        return f"Total profit: ₹{total:,.0f}"

    # --- Revenue by region ---
    if "region" in q and ("revenue" in q or "sales" in q):
        result = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
        lines = [f"{r}: ₹{v:,.0f}" for r, v in result.items()]
        return "Revenue by region:\n" + "\n".join(lines)

    # --- Top sales rep ---
    if ("top" in q or "best" in q) and ("rep" in q or "salesperson" in q or "sales rep" in q):
        result = df.groupby("sales_rep")["revenue"].sum().sort_values(ascending=False)
        top = result.index[0]
        return f"Top sales rep by revenue: {top} with ₹{result[top]:,.0f}"

    # --- All reps performance ---
    if "rep" in q or "salesperson" in q:
        result = df.groupby("sales_rep").agg(
            total_revenue=("revenue", "sum"),
            total_profit=("profit", "sum"),
            orders=("order_id", "count")
        ).sort_values("total_revenue", ascending=False)
        lines = [f"{r}: Revenue ₹{row.total_revenue:,.0f} | Profit ₹{row.total_profit:,.0f} | Orders {row.orders}"
                 for r, row in result.iterrows()]
        return "Sales rep performance:\n" + "\n".join(lines)

    # --- Revenue by product ---
    if "product" in q and ("revenue" in q or "sales" in q or "top" in q or "best" in q):
        result = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
        lines = [f"{p}: ₹{v:,.0f}" for p, v in result.items()]
        return "Revenue by product:\n" + "\n".join(lines)

    # --- Revenue by category ---
    if "category" in q:
        result = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
        lines = [f"{c}: ₹{v:,.0f}" for c, v in result.items()]
        return "Revenue by category:\n" + "\n".join(lines)

    # --- Monthly trend ---
    if "month" in q or "monthly" in q or "trend" in q:
        result = df.groupby(df["date"].dt.to_period("M"))["revenue"].sum()
        lines = [f"{str(m)}: ₹{v:,.0f}" for m, v in result.items()]
        return "Monthly revenue trend:\n" + "\n".join(lines)

    # --- Quarterly ---
    if "quarter" in q or "quarterly" in q:
        result = df.groupby("quarter")["revenue"].sum()
        lines = [f"{q_}: ₹{v:,.0f}" for q_, v in result.items()]
        return "Quarterly revenue:\n" + "\n".join(lines)

    # --- Profit margin ---
    if "margin" in q or "profit margin" in q:
        df["margin_pct"] = (df["profit"] / df["revenue"] * 100).round(2)
        avg = df["margin_pct"].mean().round(2)
        by_product = df.groupby("product")["margin_pct"].mean().round(2).sort_values(ascending=False)
        lines = [f"{p}: {v}%" for p, v in by_product.items()]
        return f"Overall average profit margin: {avg}%\n\nBy product:\n" + "\n".join(lines)

    # --- Top customers ---
    if "customer" in q:
        result = df.groupby("customer")["revenue"].sum().sort_values(ascending=False).head(5)
        lines = [f"{c}: ₹{v:,.0f}" for c, v in result.items()]
        return "Top 5 customers by revenue:\n" + "\n".join(lines)

    # --- General summary ---
    total_rev = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = len(df)
    top_rep = df.groupby("sales_rep")["revenue"].sum().idxmax()
    top_product = df.groupby("product")["revenue"].sum().idxmax()
    top_region = df.groupby("region")["revenue"].sum().idxmax()

    return (
        f"Sales Data Summary:\n"
        f"Total Revenue: ₹{total_rev:,.0f}\n"
        f"Total Profit: ₹{total_profit:,.0f}\n"
        f"Total Orders: {total_orders}\n"
        f"Top Sales Rep: {top_rep}\n"
        f"Best Selling Product: {top_product}\n"
        f"Best Performing Region: {top_region}"
    )
