# tracker.py
# Author: Stephen Ongoma
# Finance Tracker v2 - Income and Balance Tracking
# This version allows you to add income and expenses, view all transactions, and see your balance summary.

import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()

# Ensure the transactions table exists (and includes 'type' column)
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    description TEXT,
                    amount REAL,
                    type TEXT DEFAULT 'expense'
                )''')
conn.commit()

def add_transaction():
    """Add a new income or expense."""
    print("\nAdd a new transaction")
    trans_type = input("Enter type (income/expense): ").strip().lower()

    if trans_type not in ['income', 'expense']:
        print("❌ Invalid type! Please enter 'income' or 'expense'.")
        return

    category = input("Enter category (e.g., salary, food, rent): ").strip()
    description = input("Enter description: ").strip()
    try:
        amount = float(input("Enter amount (Ksh): "))
    except ValueError:
        print("❌ Invalid amount. Please enter a number.")
        return

    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("INSERT INTO transactions (date, category, description, amount, type) VALUES (?, ?, ?, ?, ?)",
                   (date, category, description, amount, trans_type))
    conn.commit()
    print(f"✅ {trans_type.capitalize()} added successfully!")

def view_summary():
    """Display total income, total expenses, and balance."""
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expense = cursor.fetchone()[0] or 0.0

    balance = total_income - total_expense

    print("\n===== Financial Summary =====")
    print(f"Total Income : Ksh {total_income:,.2f}")
    print(f"Total Expense: Ksh {total_expense:,.2f}")
    print(f"Current Balance: Ksh {balance:,.2f}")
    print("=============================\n")

def view_all():
    """Show all transactions in the database."""
    print("\n--- All Transactions ---")
    cursor.execute("SELECT date, category, description, amount, type FROM transactions ORDER BY date DESC")
    records = cursor.fetchall()

    if not records:
        print("No transactions found.")
        return

    for row in records:
        date, category, description, amount, trans_type = row
        print(f"{date} | {category} | {description} | {trans_type.capitalize()} | Ksh {amount:,.2f}")

def main():
    """Main program menu."""
    while True:
        print("\n--- Finance Tracker Menu ---")
        print("1. Add a transaction")
        print("2. View summary")
        print("3. View all transactions")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_summary()
        elif choice == "3":
            view_all()
        elif choice == "4":
            print("👋 Goodbye, Stephen! Keep managing your money wisely.")
            break
        else:
            print("❌ Invalid choice! Try again.")

    conn.close()

if __name__ == "__main__":
    main()
