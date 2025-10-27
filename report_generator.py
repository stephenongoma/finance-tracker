# report_generator.py
# Author: Stephen Ongoma
# Finance Tracker v3.1 - Monthly PDF Report Generator
# ---------------------------------------------------------------
# This script generates a professional monthly finance report as a PDF.
# It includes:
# - Income, Expense, and Balance Summary
# - Top 3 Expense Categories
# - Monthly Spending Chart
# ---------------------------------------------------------------

import sqlite3
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import matplotlib.pyplot as plt

# Paths
DB_PATH = "finance.db"
EXPORT_DIR = "data"
os.makedirs(EXPORT_DIR, exist_ok=True)

def load_data():
    """Load all transactions from the SQLite database into a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, category, description, amount, type FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def generate_monthly_summary(df):
    """Generate summary statistics for the current month."""
    now = datetime.now()
    this_month = df[df['date'].dt.month == now.month]

    total_income = this_month.loc[this_month['type'] == 'income', 'amount'].sum()
    total_expense = this_month.loc[this_month['type'] == 'expense', 'amount'].sum()
    balance = total_income - total_expense

    top_categories = (
        this_month[this_month['type'] == 'expense']
        .groupby('category')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )

    summary = {
        "month": now.strftime("%B %Y"),
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "top_categories": top_categories
    }
    return summary, this_month

def plot_monthly_chart(df, filename):
    """Plot income vs expense chart for the month."""
    df['day'] = df['date'].dt.day
    daily_summary = df.groupby(['day', 'type'])['amount'].sum().unstack(fill_value=0)

    plt.figure(figsize=(8, 4))
    daily_summary.plot(kind='bar', stacked=True)
    plt.title("Daily Income vs Expense")
    plt.xlabel("Day of Month")
    plt.ylabel("Amount (Ksh)")
    plt.legend(title="Type")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    chart_path = os.path.join(EXPORT_DIR, filename)
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def generate_pdf_report(summary, chart_path):
    """Create the PDF report with all details."""
    filename = f"Finance_Report_{summary['month'].replace(' ', '_')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<b>Finance Tracker Monthly Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Report Period:</b> {summary['month']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Summary Table
    data = [
        ["Total Income (Ksh)", f"{summary['total_income']:,.2f}"],
        ["Total Expense (Ksh)", f"{summary['total_expense']:,.2f}"],
        ["Balance (Ksh)", f"{summary['balance']:,.2f}"]
    ]
    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Top 3 categories
    elements.append(Paragraph("<b>Top 3 Spending Categories</b>", styles["Heading3"]))
    if summary['top_categories'].empty:
        elements.append(Paragraph("No expense data for this month.", styles["Normal"]))
    else:
        cat_data = [[cat, f"Ksh {amt:,.2f}"] for cat, amt in summary['top_categories'].items()]
        cat_table = Table(cat_data, hAlign="LEFT")
        cat_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        elements.append(cat_table)

    elements.append(Spacer(1, 20))

    # Add chart
    elements.append(Paragraph("<b>Daily Income vs Expense Chart</b>", styles["Heading3"]))
    elements.append(Image(chart_path, width=400, height=200))

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF report generated successfully: {filepath}")

def main():
    df = load_data()

    if df.empty:
        print("⚠️ No data available. Please add transactions using tracker.py.")
        return

    summary, month_data = generate_monthly_summary(df)
    chart_path = plot_monthly_chart(month_data, "temp_chart.png")
    generate_pdf_report(summary, chart_path)

if __name__ == "__main__":
    main()
