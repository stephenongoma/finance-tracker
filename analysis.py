# analysis.py
# Author: Stephen Ongoma
# Finance Tracker v3.0 - Smart Insights and Analytics
# ---------------------------------------------------------------
# Features:
# - Load and summarize financial data
# - Smart insights (top categories, daily avg, savings trend)
# - Visualizations and CSV export
# ---------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from database import connect, check_monthly_budget

# Export folder
EXPORT_DIR = "data"
os.makedirs(EXPORT_DIR, exist_ok=True)

def load_data():
    """Load all transactions from the SQLite database into a pandas DataFrame."""
    conn = connect()  # Use the centralized connect function
    # Query columns that exist in the database schema
    query = "SELECT date, category, amount, type FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

# 🧠 NEW: Generate Smart Insights
def generate_insights(df):
    """Provide key insights like top categories, daily average, and savings trends."""
    if df.empty:
        print("⚠️ No data available for insights.")
        return

    # Current month filter
    now = datetime.now()
    this_month = df[df['date'].dt.month == now.month]

    if this_month.empty:
        print("\n📅 No transactions for this month yet.")
        return

    # Basic stats
    income = this_month.loc[this_month['type'] == 'income', 'amount'].sum()
    expense = this_month.loc[this_month['type'] == 'expense', 'amount'].sum()
    balance = income - expense
    avg_daily_expense = this_month.loc[this_month['type'] == 'expense', 'amount'].sum() / max(1, this_month['date'].dt.day.nunique())

    # Top 3 categories
    top_categories = (
        this_month[this_month['type'] == 'expense']
        .groupby('category')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )

    # Compare with last month (if data available)
    last_month_num = now.month - 1 if now.month > 1 else 12
    last_month = df[df['date'].dt.month == last_month_num]
    if not last_month.empty:
        last_income = last_month.loc[last_month['type'] == 'income', 'amount'].sum()
        last_expense = last_month.loc[last_month['type'] == 'expense', 'amount'].sum()
        savings_change = ((balance - (last_income - last_expense)) / max(1, (last_income - last_expense))) * 100
    else:
        savings_change = None

    print("\n===== 💡 SMART FINANCIAL INSIGHTS =====")
    print(f"📆 Month: {now.strftime('%B %Y')}")
    print(f"💰 Total Income: Ksh {income:,.2f}")
    print(f"💸 Total Expense: Ksh {expense:,.2f}")
    print(f"🪙 Balance: Ksh {balance:,.2f}")
    print(f"📊 Average Daily Spending: Ksh {avg_daily_expense:,.2f}")

    # 🧠 NEW: Budget Insights
    budget_status = check_monthly_budget()
    if budget_status:
        print("\n🎯 Budget Status:")
        print(f"   - Budget Set: Ksh {budget_status['budget']:,.2f}")
        print(f"   - Spent: Ksh {budget_status['spent']:,.2f} ({budget_status['percent_used']:.1f}% used)")
        if budget_status['is_exceeded']:
            print(f"   - ⚠️  You are Ksh {abs(budget_status['remaining']):,.2f} over budget!")
        else:
            print(f"   - Remaining: Ksh {budget_status['remaining']:,.2f}")
    print("\n🏆 Top 3 Spending Categories:")
    for category, amount in top_categories.items():
        print(f"   - {category}: Ksh {amount:,.2f}")

    if savings_change is not None:
        trend = "increased" if savings_change > 0 else "decreased"
        print(f"\n📈 Savings have {trend} by {abs(savings_change):.1f}% compared to last month.")
    else:
        print("\n📈 No previous month data available for comparison.")

    print("========================================\n")

def summarize_data(df):
    """Generate and print basic financial summaries."""
    total_income = df.loc[df['type'] == 'income', 'amount'].sum()
    total_expense = df.loc[df['type'] == 'expense', 'amount'].sum()
    balance = total_income - total_expense

    print("\n===== Financial Summary =====")
    print(f"Total Income : Ksh {total_income:,.2f}")
    print(f"Total Expense: Ksh {total_expense:,.2f}")
    print(f"Balance      : Ksh {balance:,.2f}")
    print("=============================\n")

def plot_income_vs_expense(df):
    """Plot monthly income vs expense bar chart."""
    df['month'] = df['date'].dt.to_period('M')
    monthly_summary = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)

    monthly_summary.plot(kind='bar', figsize=(10, 6))
    plt.title("Monthly Income vs Expense")
    plt.xlabel("Month")
    plt.ylabel("Amount (Ksh)")
    plt.legend(title="Type")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def plot_expense_distribution(df):
    """Plot a pie chart showing expense distribution by category."""
    expense_df = df[df['type'] == 'expense']
    if expense_df.empty:
        print("⚠️ No expense data to visualize yet.")
        return

    category_sum = expense_df.groupby('category')['amount'].sum()
    plt.figure(figsize=(7, 7))
    plt.pie(category_sum, labels=category_sum.index, autopct='%1.1f%%', startangle=90)
    plt.title("Expense Distribution by Category")
    plt.tight_layout()
    plt.show()

def export_to_csv(df):
    """Export all transactions to a CSV file in the /data directory."""
    if df.empty:
        print("⚠️ No data available to export.")
        return

    filename = f"transactions_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Data exported successfully to: {filepath}")

def export_current_month_to_csv(df):
    """Export only the current month's transactions to a CSV file."""
    now = datetime.now()
    this_month_df = df[df['date'].dt.month == now.month]

    if this_month_df.empty:
        print(f"⚠️ No transactions found for {now.strftime('%B %Y')} to export.")
        return

    filename = f"transactions_{now.strftime('%Y-%m')}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    this_month_df.to_csv(filepath, index=False)
    print(f"✅ Current month's data exported successfully to: {filepath}")

def main():
    print("📊 Loading data from database...")
    df = load_data()

    if df.empty:
        print("No transactions found. Please add some data first using tracker.py.")
        return

    summarize_data(df)
    generate_insights(df)  # 🧠 show insights immediately

    while True:
        print("\n--- Analysis Menu ---")
        print("1. View monthly income vs expense chart")
        print("2. View expense distribution by category")
        print("3. Export all transactions to CSV")
        print("4. Export current month's transactions to CSV")
        print("5. Exit")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            plot_income_vs_expense(df)
        elif choice == "2":
            plot_expense_distribution(df)
        elif choice == "3":
            export_to_csv(df)
        elif choice == "4": # New option
            export_current_month_to_csv(df)
        elif choice == "5":
            print("👋 Exiting analysis module.")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
