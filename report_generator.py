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
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import matplotlib.pyplot as plt
from database import connect, check_monthly_budget

# --- Configuration ---
EXPORT_DIR = "data"
LOGO_PATH = "assets/logo.png"  # Place your logo here
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs("assets", exist_ok=True)

# --- Color Theme ---
THEME = {
    "primary": colors.HexColor("#1E3A8A"),      # Deep Blue
    "secondary": colors.HexColor("#EFF6FF"),    # Very Light Blue
    "text": colors.HexColor("#1F2937"),         # Dark Gray
    "accent_good": colors.HexColor("#10B981"),  # Green
    "accent_bad": colors.HexColor("#EF4444"),    # Red
    "grid": colors.HexColor("#D1D5DB"),         # Light Gray for grids
}

def load_data():
    """Load all transactions from the SQLite database into a pandas DataFrame."""
    conn = connect()
    query = "SELECT date, category, amount, type FROM transactions"
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
    daily_summary.plot(kind='bar', stacked=True, color=[THEME["accent_good"], THEME["accent_bad"]])
    plt.title("Daily Income vs Expense")
    plt.xlabel("Day of Month")
    plt.ylabel("Amount (Ksh)")
    plt.legend(title="Type", facecolor=THEME["secondary"])
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    chart_path = os.path.join(EXPORT_DIR, filename)
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def calculate_financial_health_score(summary, budget_status):
    """Calculate a financial health score out of 100."""
    score = 0
    income = summary['total_income']
    expense = summary['total_expense']

    # 1. Savings Rate (60 points)
    if income > 0:
        savings_rate = (income - expense) / income
        if savings_rate >= 0.2:  # Saving 20% or more
            score += 60
        elif savings_rate > 0:
            score += (savings_rate / 0.2) * 60  # Prorated score

    # 2. Budget Adherence (40 points)
    if budget_status:
        budget = budget_status['budget']
        if budget > 0 and expense <= budget:
            score += 40
        elif budget > 0 and expense > budget:
            # Penalize for going over budget
            overage_ratio = (expense - budget) / budget
            penalty = min(overage_ratio * 40, 40) # Cap penalty at 40
            score += (40 - penalty)

    score = max(0, min(100, int(score))) # Ensure score is between 0 and 100

    if score >= 80:
        rating = ("Excellent", THEME["accent_good"])
    elif score >= 60:
        rating = ("Good", colors.orange) # Keep orange for 'Good' as it stands out
    else:
        rating = ("Needs Improvement", THEME["accent_bad"])
    return score, rating

def generate_pdf_report(summary, budget_status, health_score, chart_path):
    """Create the PDF report with all details."""
    filename = f"Finance_Report_{summary['month'].replace(' ', '_')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Header with Logo ---
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=50, height=50)
        header_data = [[logo, Paragraph("<b>Finance Tracker Monthly Report</b>", styles["Title"])]]
        header_table = Table(header_data, colWidths=[60, None], style=[
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            # No borders
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ])
        elements.append(header_table)
    else:
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
        ("BACKGROUND", (0, 0), (0, -1), THEME["secondary"]),
        ("TEXTCOLOR", (0, 0), (-1, -1), THEME["text"]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, THEME["grid"]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # Budget Status
    elements.append(Paragraph("<b>Budget Status</b>", styles["Heading3"]))
    if budget_status:
        remaining_color = THEME["accent_bad"] if budget_status['is_exceeded'] else THEME["accent_good"]
        budget_data = [
            ["Monthly Budget (Ksh)", f"{budget_status['budget']:,.2f}"],
            ["Total Spent (Ksh)", f"{budget_status['spent']:,.2f}"],
            ["Remaining (Ksh)", Paragraph(f"<font color='{remaining_color}'>{budget_status['remaining']:,.2f}</font>", styles["Normal"])]
        ]
        budget_table = Table(budget_data, hAlign="LEFT")
        budget_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, THEME["grid"]),
            ("BACKGROUND", (0, 0), (0, -1), THEME["secondary"]),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(budget_table)
        if budget_status['is_exceeded']:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"⚠️ You have exceeded your budget by Ksh {abs(budget_status['remaining']):,.2f}.", styles["Normal"]))
    else:
        elements.append(Paragraph("No budget has been set for this month.", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # Financial Health Score
    score, (rating_text, rating_color) = health_score
    elements.append(Paragraph("<b>Financial Health Score</b>", styles["Heading3"]))
    score_data = [
        ["Health Score", f"{score} / 100"],
        ["Rating", Paragraph(f"<font color='{rating_color}'>{rating_text}</font>", styles["Normal"])]
    ]
    score_table = Table(score_data, hAlign="LEFT")
    score_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, THEME["grid"]),
        ("BACKGROUND", (0, 0), (0, -1), THEME["secondary"]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(score_table)

    elements.append(Spacer(1, 20))

    # Top 3 categories
    elements.append(Paragraph("<b>Top 3 Spending Categories</b>", styles["Heading3"]))
    if summary['top_categories'].empty:
        elements.append(Paragraph("No expense data for this month.", styles["Normal"]))
    else:
        cat_data = [[cat, f"Ksh {amt:,.2f}"] for cat, amt in summary['top_categories'].items()]
        cat_table = Table(cat_data, hAlign="LEFT")
        cat_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, THEME["grid"]),
            ("BACKGROUND", (0, 0), (0, -1), THEME["secondary"]),
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
    budget_status = check_monthly_budget()
    health_score = calculate_financial_health_score(summary, budget_status)
    chart_path = plot_monthly_chart(month_data, "temp_chart.png")
    generate_pdf_report(summary, budget_status, health_score, chart_path)

if __name__ == "__main__":
    main()
