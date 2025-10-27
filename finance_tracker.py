from datetime import datetime
from database import (
    create_table,
    create_budget_table,
    add_transaction as db_add_transaction,
    get_summary,
    get_expenses_by_category,
    get_all_transactions,
    set_monthly_budget,
    check_monthly_budget,
)

def main():
    """
    Display the main menu and handle user choices.
    The program loops until the user chooses to exit.
    """
    while True:
        print("\n" + "=" * 40)
        print("💰 UNIFIED FINANCE TRACKER")
        print("=" * 40)
        print("1. Add Transaction")
        print("3. View Summary")
        print("4. View All Transactions")
        print("5. View Expenses by Category")
        print("6. Set Monthly Budget")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            # This option is now part of 'Add Transaction'
            # Kept for backward compatibility or can be removed.
            # For now, let's point it to the new function.
            add_transaction()
        elif choice == "3":
            view_summary()
        elif choice == "4":
            view_all_transactions()
        elif choice == "5":
            view_expenses_by_category()
        elif choice == "6":
            set_budget()
        elif choice == "7":
            print("\n✅ Exiting program. Goodbye!\n")
            break
        else:
            print("\n⚠️ Invalid choice! Please select a number between 1 and 7.")


def add_transaction():
    """Add an income or expense record."""
    print("\n➡️  Add a new transaction")
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

    db_add_transaction(trans_type, category, amount)
    print(f"✅ {trans_type.capitalize()} added successfully!")


def set_budget():
    """Set or update a monthly budget."""
    month = datetime.now().strftime("%Y-%m")
    try:
        amount = float(input("Enter your monthly budget for this month (Ksh): "))
    except ValueError:
        print("❌ Invalid number.")
        return

    set_monthly_budget(month, amount)
    print(f"✅ Budget set for {month}: Ksh {amount:,.2f}")

def view_summary():
    """
    Display income, expenses, balance, and budget alert.
    """
    total_income, total_expense, balance = get_summary()

    print("\n===== Financial Summary =====")
    print(f"Total Income   : Ksh {total_income:,.2f}")
    print(f"Total Expenses : Ksh {total_expense:,.2f}")
    print(f"Current Balance: Ksh {balance:,.2f}")
    print("-----------------------------")

    budget_status = check_monthly_budget()
    if budget_status:
        if budget_status["is_exceeded"]:
            print(f"⚠️   ALERT: You've exceeded your budget of Ksh {budget_status['budget']:,.2f} by Ksh {abs(budget_status['remaining']):,.2f}!")
        else:
            print(f"💰   You’ve used {budget_status['percent_used']:.1f}% of your budget. Remaining: Ksh {budget_status['remaining']:,.2f}")
    else:
        print("💡   No budget set for this month. Use option '6' to set one.")
    print("=============================\n")

def view_all_transactions():
    """Display all transactions."""
    print("\n--- All Transactions ---")
    records = get_all_transactions()
    if not records:
        print("No transactions found.")
        return

    print(f"{'Date':<12} | {'Category':<15} | {'Type':<8} | {'Amount (Ksh)':>15}")
    print("-" * 60)
    for date, category, amount, t_type in records:
        print(f"{date.split(' ')[0]:<12} | {category:<15} | {t_type.capitalize():<8} | {amount:>15,.2f}")

def view_expenses_by_category():
    """
    Display a list of total expenses grouped by category.
    """
    expenses = get_expenses_by_category()
    print("\n📂 EXPENSES BY CATEGORY")
    print("-" * 40)

    if not expenses:
        print("No expense records found.")
    else:
        print(f"{'Category':<20} | {'Total Spent (Ksh)':>15}")
        print("-" * 40)
        for category, total in expenses:
            print(f"{category:<20} | {total:>15,.2f}")

    print("-" * 40)

# Entry point of the program
if __name__ == "__main__":
    # Ensure all tables exist on startup
    create_table()
    create_budget_table()
    main()
