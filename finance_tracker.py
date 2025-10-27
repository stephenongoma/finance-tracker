from datetime import datetime
import pandas as pd
import os
from database import (
    create_table,
    create_budget_table,
    add_transaction as db_add_transaction,
    get_summary,
    get_expenses_by_category,
    get_all_transactions,
    set_monthly_budget,
    check_monthly_budget,
    get_transaction_by_id,
    delete_transaction_by_id,
    update_transaction_by_id,
    add_bulk_transactions,
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
        print("7. Manage Transactions")
        print("8. Import from CSV")
        print("9. Exit")

        choice = input("\nEnter your choice (1-9): ").strip()

        if choice == "1":
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
            manage_transactions()
        elif choice == "8":
            import_from_csv()
        elif choice == "9":
            print("\n✅ Exiting program. Goodbye!\n")
            break
        else:
            print("\n⚠️ Invalid choice! Please select a number between 1 and 9.")


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

    print(f"{'ID':<5} | {'Date':<12} | {'Category':<15} | {'Type':<8} | {'Amount (Ksh)':>15}")
    print("-" * 70)
    for trans_id, date, category, amount, t_type in records:
        print(f"{trans_id:<5} | {date.split(' ')[0]:<12} | {category:<15} | {t_type.capitalize():<8} | {amount:>15,.2f}")
    return True # Indicate that records were found and displayed

def manage_transactions():
    """Display transactions and provide options to edit or delete."""
    print("\n--- Manage Transactions ---")
    if not view_all_transactions(): # Display all transactions and check if any exist
        return

    try:
        trans_id = int(input("\nEnter the ID of the transaction to manage (or 0 to cancel): ").strip())
        if trans_id == 0:
            return
    except ValueError:
        print("❌ Invalid ID. Please enter a number.")
        return

    # Check if the transaction ID is valid
    if not get_transaction_by_id(trans_id):
        print("❌ Transaction ID not found.")
        return

    print("\nSelect an action:")
    print("1. Edit Transaction")
    print("2. Delete Transaction")
    print("3. Cancel")
    choice = input("Enter your choice (1-3): ").strip()

    if choice == "1":
        edit_transaction(trans_id)
    elif choice == "2":
        delete_transaction(trans_id)
    else:
        print("Action canceled.")

def edit_transaction(trans_id):
    """Handle the logic for editing a transaction."""
    print(f"\n✏️  Editing Transaction ID: {trans_id}")
    new_type = input("Enter new type (income/expense): ").strip().lower()
    if new_type not in ['income', 'expense']:
        print("❌ Invalid type.")
        return

    new_category = input("Enter new category: ").strip()
    try:
        new_amount = float(input("Enter new amount (Ksh): "))
    except ValueError:
        print("❌ Invalid amount.")
        return

    update_transaction_by_id(trans_id, new_type, new_category, new_amount)
    print("✅ Transaction updated successfully!")

def delete_transaction(trans_id):
    """Handle the logic for deleting a transaction."""
    confirm = input(f"❓ Are you sure you want to delete transaction ID {trans_id}? (y/n): ").strip().lower()
    if confirm == 'y':
        delete_transaction_by_id(trans_id)
        print("✅ Transaction deleted successfully!")
    else:
        print("Deletion canceled.")

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

def import_from_csv():
    """Import transactions from a user-specified CSV file."""
    print("\n--- Import Transactions from CSV ---")
    print("Your CSV file should have the columns: 'date', 'type', 'category', 'amount'")
    filepath = input("Enter the full path to your CSV file: ").strip()

    if not os.path.exists(filepath):
        print(f"❌ Error: File not found at '{filepath}'")
        return

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return

    required_columns = {'type', 'category', 'amount'}
    if not required_columns.issubset(df.columns):
        print(f"❌ CSV must contain the following columns: {', '.join(required_columns)}")
        return

    transactions_to_add = []
    for index, row in df.iterrows():
        trans_type = row['type'].lower()
        category = row['category']
        amount = row['amount']

        # Use date from CSV if available, otherwise use current date
        if 'date' in df.columns and pd.notna(row['date']):
            try:
                # Attempt to parse date, fallback to now if format is wrong
                date_str = pd.to_datetime(row['date']).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Basic validation
        if trans_type not in ['income', 'expense'] or not isinstance(amount, (int, float)):
            print(f"⚠️  Skipping invalid row {index + 1}: type='{trans_type}', amount='{amount}'")
            continue

        transactions_to_add.append((trans_type, category, amount, date_str))

    if transactions_to_add:
        add_bulk_transactions(transactions_to_add)
        print(f"\n✅ Successfully imported {len(transactions_to_add)} transactions!")
    else:
        print("⚠️ No valid transactions found to import.")

# Entry point of the program
if __name__ == "__main__":
    # Ensure all tables exist on startup
    create_table()
    create_budget_table()
    main()
