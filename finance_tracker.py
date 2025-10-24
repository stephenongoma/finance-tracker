from database import (
    create_table,
    add_transaction,
    get_summary,
    get_expenses_by_category
)

# Create the database table automatically at startup
create_table()


def main_menu():
    """
    Display the main menu and handle user choices.
    The program loops until the user chooses to exit.
    """
    while True:
        print("\n" + "=" * 40)
        print("💰 PERSONAL FINANCE TRACKER")
        print("=" * 40)
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Summary")
        print("4. View Expenses by Category")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            add_income()
        elif choice == "2":
            add_expense()
        elif choice == "3":
            view_summary()
        elif choice == "4":
            view_expenses_by_category()
        elif choice == "5":
            print("\n✅ Exiting program. Goodbye!\n")
            break
        else:
            print("\n⚠️ Invalid choice! Please select a number between 1 and 5.")


def add_income():
    """
    Add a new income transaction to the database.
    """
    try:
        category = input("\nEnter income category (e.g., Salary, Bonus): ").strip()
        amount = float(input("Enter amount: "))
        add_transaction("income", category, amount)
        print(f"✅ Income of {amount:.2f} added under '{category}'.")
    except ValueError:
        print("⚠️ Invalid amount! Please enter a numeric value.")


def add_expense():
    """
    Add a new expense transaction to the database.
    """
    try:
        category = input("\nEnter expense category (e.g., Food, Transport): ").strip()
        amount = float(input("Enter amount: "))
        add_transaction("expense", category, amount)
        print(f"✅ Expense of {amount:.2f} added under '{category}'.")
    except ValueError:
        print("⚠️ Invalid amount! Please enter a numeric value.")


def view_summary():
    """
    Display the total income, expenses, and balance.
    """
    income, expense, balance = get_summary()
    print("\n📊 FINANCIAL SUMMARY")
    print("-" * 30)
    print(f"Total Income   : {income:.2f}")
    print(f"Total Expenses : {expense:.2f}")
    print(f"Current Balance: {balance:.2f}")
    print("-" * 30)


def view_expenses_by_category():
    """
    Display a list of total expenses grouped by category.
    """
    expenses = get_expenses_by_category()
    print("\n📂 EXPENSES BY CATEGORY")
    print("-" * 30)

    if not expenses:
        print("No expense records found.")
    else:
        for category, total in expenses:
            print(f"{category:<15} : {total:.2f}")

    print("-" * 30)


# Entry point of the program
if __name__ == "__main__":
    main_menu()
