# analysis.py
# Author: Stephen Ongoma
# Finance Tracker v2.3 - Data Analysis and Export Module
# ---------------------------------------------------------------
# Features:
# - Load and summarize financial data
# - Visualize income vs expense and spending by category
# - Export data to CSV for external analysis
# ---------------------------------------------------------------

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Database path
DB_PATH = "finance.db"
EXPORT_DIR = "data"

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

def load_data():
    """Load all transactions from the SQLite database into a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT date, category, description, amount, type FROM transactions"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def summarize_data(df):
    """Generate and print basic financial summaries."""
    total_income = df.loc[df['type'] == 'income', 'amount'].sum()
    total_expense = df.loc[df['type'] == 'expense', 'amount'].sum()
    balance = total_income - total_expense

    print("\n===== Financial Summary =====")
    print(f"Total Income : Ksh {total_income:,.2f}")
    print(f"Total Expense: Ksh {total_expense:,.2f}")
    print(f"Balance      : Ksh {balance:,.2f}")

    if not df[df['type'] == 'expense'].empty:
        top_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().idxmax()
        print(f"Highest Spending Category: {top_category}")
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

    # Create a timestamped filename
    filename = f"transactions_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    df.to_csv(filepath, index=False)
    print(f"✅ Data exported successfully to: {filepath}")

def main():
    print("📊 Loading data from database...")
    df = load_data()

    if df.empty:
        print("No transactions found. Please add some data first using tracker.py.")
        return

    summarize_data(df)

    while True:
        print("\n--- Analysis Menu ---")
        print("1. View monthly income vs expense chart")
        print("2. View expense distribution by category")
        print("3. Export all transactions to CSV")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            plot_income_vs_expense(df)
        elif choice == "2":
            plot_expense_distribution(df)
        elif choice == "3":
            export_to_csv(df)
        elif choice == "4":
            print("👋 Exiting analysis module.")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
