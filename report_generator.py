# report_generator.py
# Author: Stephen Ongoma
# Finance Tracker v3.5 - Monthly PDF Report Generator
# ---------------------------------------------------------------
# Generates a professional monthly financial report
# Includes summaries, insights, and charts
# ---------------------------------------------------------------

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

DB_PATH = "finance.db"
REPORTS_DIR = "data"

# Ensure data folder exists
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_data():
    """Load all transactions from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, category, description, amount, type FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def generate_charts(df, month_str):
    """Generate charts for the PDF report."""
    df['month'] = df['date'].dt.to_period('M')

    # Bar chart: Monthly income vs expense
    monthly_summary = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
    plt.figure(figsize=(6, 4))
    monthly_summary.plot(kind='bar')
    plt.title("Monthly Income vs Expense")
    plt.xlabel("Month")
    plt.ylabel("Amount (Ksh)")
    plt.tight_layout()
    bar_chart_path = os.path.join(REPORTS_DIR, f"income_expense_chart_{month_str}.png")
    plt.savefig(bar_chart_path)
    plt.close()

    # Pie chart: Expense by category
    expense_df = df[df['type'] == 'expense']
    pie_chart_path = None
    if not expense_df.empty:
        category_sum = expense_df.groupby('category')['amount'].sum()
        plt.figure(figsize=(5, 5))
        plt.pie(category_sum, labels=category_sum.index, autopct='%1.1f%%', startangle=90)
        plt.title("Expense Distribution by Category")
        pie_chart_path = os.path.join(REPORTS_DIR, f"expense_pie_chart_{month_str}.png")
        plt.savefig(pie_chart_path)
        plt.close()

    return bar_chart_path, pie_chart_path

def generate_pdf(df):
    """Generate a professional monthly financial report."""
    now = datetime.now()
    month_str = now.strftime("%B_%Y")
    report_path = os.path.join(REPORTS_DIR, f"monthly_report_{month_str}.pdf")

    # Filter current month data
    this_month = df[df['date'].dt.month == now.month]
    if this_month.empty:
        print("⚠️ No transactions for this month. Report not created.")
        return

    # Summary
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

    # Generate charts
    bar_chart, pie_chart = generate_charts(df, month_str)

    # --- PDF Layout ---
    doc = SimpleDocTemplate(report_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<b>Finance Tracker Monthly Report</b>", styles['Title']))
    elements.append(Paragraph(f"Report Date: {now.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary
    summary_data = [
        ["Total Income", f"Ksh {total_income:,.2f}"],
        ["Total Expense", f"Ksh {total_expense:,.2f}"],
        ["Balance", f"Ksh {balance:,.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # Top categories
    elements.append(Paragraph("<b>Top 3 Spending Categories</b>", styles['Heading2']))
    if top_categories.empty:
        elements.append(Paragraph("No expenses recorded this month.", styles['Normal']))
    else:
        data = [["Category", "Amount (Ksh)"]]
        for cat, amt in top_categories.items():
            data.append([cat, f"{amt:,.2f}"])
        cat_table = Table(data, colWidths=[200, 200])
        cat_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        elements.append(cat_table)

    elements.append(Spacer(1, 20))

    # Add charts
    elements.append(Paragraph("<b>Visual Insights</b>", styles['Heading2']))
    if bar_chart:
        elements.append(Image(bar_chart, width=400, height=250))
        elements.append(Spacer(1, 12))
    if pie_chart:
        elements.append(Image(pie_chart, width=350, height=250))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<i>Generated automatically by Stephen Ongoma’s Finance Tracker</i>", styles['Normal']))

    doc.build(elements)
    print(f"✅ PDF Report successfully created: {report_path}")

def main():
    print("📄 Generating Monthly PDF Report...")
    df = load_data()
    generate_pdf(df)

if __name__ == "__main__":
    main()
