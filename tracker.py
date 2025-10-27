# tracker.py
# Author: Stephen Ongoma
# Finance Tracker v2.1 - Budget Goals and Alerts

import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('finance.db')
cursor = conn.cursor()

# Ensure transactions table exists
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    description TEXT,
                    amount REAL,
                    type TEXT DEFAULT 'expense'
                )''')

# Ensure budget table exists
cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month TEXT,
                    amount REAL
                )''')
conn.commit()

def add_transaction():
    """Add an income or expense record."""
    print("\nAdd a new transaction")
    trans_type = input("Enter type (income/expense): ").strip().lower()
    if trans_type not in ['income', 'expense']:
        print("❌ Invalid type. Must be 'income' or 'expense'.")
        return

    category = input("Enter category (e.g. food, rent, salary): ").strip()
    description = input("Enter description: ").strip()
    try:
        amount = float(input("Enter amount (Ksh): "))
    except ValueError:
        print("❌ Please enter a valid number for amount.")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO transactions (date, category, description, amount, type) VALUES (?, ?, ?, ?, ?)",
                   (date, category, description, amount, trans_type))
    conn.commit()

    print(f"✅ {trans_type.capitalize()} added successfully!")

def set_budget():
    """Set or update a monthly budget."""
    month = datetime.now().strftime("%Y-%m")
    try:
        amount = float(input("Enter your monthly budget (Ksh): "))
    except ValueError:
        print("❌ Invalid number.")
        return

    cursor.execute("DELETE FROM budget WHERE month=?", (month,))
    cursor.execute("INSERT INTO budget (month, amount) VALUES (?, ?)", (month, amount))
    conn.commit()
    print(f"✅ Budget set for {month}: Ksh {amount:,.2f}")

def check_budget():
    """Check spending against the monthly budget."""
    month = datetime.now().strftime("%Y-%m")

    cursor.execute("SELECT amount FROM budget WHERE month=?", (month,))
    row = cursor.fetchone()
    if not row:
        return None

    budget = row[0]

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND date LIKE ?", (f"{month}%",))
    total_expense = cursor.fetchone()[0] or 0.0

    percent_used = (total_expense / budget) * 100 if budget > 0 else 0
    remaining = budget - total_expense

    if total_expense >= budget:
        print(f"⚠️   ALERT: You've exceeded your budget of Ksh {budget:,.2f} by Ksh {abs(remaining):,.2f}!")
    else:
        print(f"💰   You’ve used {percent_used:.1f}% of your budget. Remaining: Ksh {remaining:,.2f}")

def view_summary():
    """Display income, expenses, balance, and budget alert."""
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    total_income = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    total_expense = cursor.fetchone()[0] or 0.0

    balance = total_income - total_expense

    print("\n===== Financial Summary =====")
    print(f"Total Income : Ksh {total_income:,.2f}")
    print(f"Total Expense: Ksh {total_expense:,.2f}")
    print(f"Current Balance: Ksh {balance:,.2f}")
    print("=============================")

    check_budget()
    print()

def view_all():
    """Display all transactions."""
    print("\n--- All Transactions ---")
    cursor.execute("SELECT date, category, description, amount, type FROM transactions ORDER BY date DESC")
    records = cursor.fetchall()
    if not records:
        print("No transactions found.")
        return

    for date, category, desc, amount, t_type in records:
        print(f"{date} | {category} | {desc} | {t_type.capitalize()} | Ksh {amount:,.2f}")

def main():
    """Main program menu."""
    while True:
        print("\n--- Finance Tracker Menu ---")
        print("1. Add a transaction")
        print("2. View summary")
        print("3. Set monthly budget")
        print("4. View all transactions")
        print("5. Exit")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_summary()
        elif choice == "3":
            set_budget()
        elif choice == "4":
            view_all()
        elif choice == "5":
            print("👋 Goodbye, Stephen! Stay within your budget!")
            break
        else:
            print("❌ Invalid choice, try again.")

    conn.close()

if __name__ == "__main__":
    main()
