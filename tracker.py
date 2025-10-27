# tracker.py
# Author: Stephen Ongoma
# Finance Tracker v2.1 - Budget Goals and Alerts
from datetime import datetime
from database import (
    add_transaction as db_add_transaction,
    get_summary,
    get_all_transactions,
    set_monthly_budget,
    check_monthly_budget,
    create_table,
    create_budget_table
)

def add_transaction():
    """Add an income or expense record."""
    print("\nAdd a new transaction")
    trans_type = input("Enter type (income/expense): ").strip().lower()
    if trans_type not in ['income', 'expense']:
        print("❌ Invalid type. Must be 'income' or 'expense'.")
        return

    category = input("Enter category (e.g., Food, Rent, Salary): ").strip()
    try:
        amount = float(input("Enter amount (Ksh): "))
    except ValueError:
        print("❌ Please enter a valid number for amount.")
        return

    # Using the function from database.py
    db_add_transaction(trans_type, category, amount)
    print(f"✅ {trans_type.capitalize()} added successfully!")

def set_budget():
    """Set or update a monthly budget."""
    month = datetime.now().strftime("%Y-%m")
    try:
        amount = float(input("Enter your monthly budget (Ksh): "))
    except ValueError:
        print("❌ Invalid number.")
        return

    set_monthly_budget(month, amount)
    print(f"✅ Budget set for {month}: Ksh {amount:,.2f}")

def check_budget():
    """Check spending against the monthly budget."""
    budget_status = check_monthly_budget()
    if budget_status:
        if budget_status["is_exceeded"]:
            print(f"⚠️   ALERT: You've exceeded your budget of Ksh {budget_status['budget']:,.2f} by Ksh {abs(budget_status['remaining']):,.2f}!")
        else:
            print(f"💰   You’ve used {budget_status['percent_used']:.1f}% of your budget. Remaining: Ksh {budget_status['remaining']:,.2f}")

def view_summary():
    """Display income, expenses, balance, and budget alert."""
    total_income, total_expense, _ = get_summary()
    balance = total_income - total_expense

    print("\n===== Financial Summary =====")
    print(f"Total Income : Ksh {total_income:,.2f}")
    print(f"Total Expense: Ksh {total_expense:,.2f}")
    print(f"Current Balance: Ksh {balance:,.2f}")
    print("-----------------------------")

    check_budget()
    print("=============================\n")

def view_all():
    """Display all transactions."""
    print("\n--- All Transactions ---")
    records = get_all_transactions()
    if not records:
        print("No transactions found.")
        return

    # Assuming get_all_transactions returns (date, category, amount, type)
    for date, category, amount, t_type in records:
        print(f"{date.split(' ')[0]} | {category:<15} | {t_type.capitalize():<8} | Ksh {amount:,.2f}")

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

if __name__ == "__main__":
    # Ensure all tables exist on startup
    create_table()
    create_budget_table()
    main()
