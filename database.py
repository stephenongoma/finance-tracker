import sqlite3
from datetime import datetime
import os

# Define the location of the database file
DB_NAME = "data/finance.db"


def connect():
    """
    Connect to the SQLite database.
    If the database file or folder doesn't exist, they will be created.
    """
    # Ensure the 'data' folder exists
    os.makedirs("data", exist_ok=True)
    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_table():
    """
    Create a table named 'transactions' if it doesn't already exist.
    Each record stores:
    - type: income or expense
    - category: what kind of spending or income (e.g. food, salary)
    - amount: numeric value
    - date: timestamp of when it was added
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def create_budget_table():
    """
    Create a table named 'budget' if it doesn't already exist.
    Each record stores:
    - month: The month in 'YYYY-MM' format
    - amount: The budgeted amount for that month
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_transaction(transaction_type, category, amount):
    """
    Insert a new transaction (income or expense) into the database.
    Parameters:
        transaction_type (str): 'income' or 'expense'
        category (str): Category name (e.g., 'Food', 'Salary')
        amount (float): Transaction amount
    """
    conn = connect()
    cursor = conn.cursor()

    # Get current date and time
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO transactions (type, category, amount, date)
        VALUES (?, ?, ?, ?)
    """, (transaction_type, category, amount, date_str))

    conn.commit()
    conn.close()

def add_bulk_transactions(transactions):
    """
    Insert multiple transactions into the database using executemany.
    Parameters:
        transactions (list): A list of tuples, where each tuple is
                             (type, category, amount, date).
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO transactions (type, category, amount, date)
        VALUES (?, ?, ?, ?)
    """, transactions)

    conn.commit()
    conn.close()


def get_summary():
    """
    Calculate total income, total expenses, and overall balance.
    Returns:
        (income, expense, balance)
    """
    conn = connect()
    cursor = conn.cursor()

    # Total income
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    income = cursor.fetchone()[0] or 0  # Default to 0 if None

    # Total expenses
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    expense = cursor.fetchone()[0] or 0

    # Remaining balance
    balance = income - expense

    conn.close()
    return income, expense, balance


def get_expenses_by_category():
    """
    Fetch and summarize all expenses grouped by category.
    Returns:
        List of tuples [(category, total_spent), ...]
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE type='expense'
        GROUP BY category
    """)

    results = cursor.fetchall()
    conn.close()

    return results

def get_all_transactions():
    """
    Fetch all transactions, ordered by date descending.
    Returns:
        List of tuples [(id, date, category, amount, type), ...]
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, date, category, amount, type
        FROM transactions
        ORDER BY date DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def set_monthly_budget(month, amount):
    """
    Set or update the budget for a given month ('YYYY-MM').
    """
    conn = connect()
    cursor = conn.cursor()
    # Use INSERT OR REPLACE to handle both new and existing budget months
    cursor.execute("""
        INSERT OR REPLACE INTO budget (month, amount)
        VALUES (?, ?)
    """, (month, amount))
    conn.commit()
    conn.close()

def check_monthly_budget():
    """
    Check current month's spending against its budget.
    Returns:
        A dictionary with budget status or None if no budget is set.
    """
    month = datetime.now().strftime("%Y-%m")
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT amount FROM budget WHERE month=?", (month,))
    budget_row = cursor.fetchone()
    if not budget_row:
        conn.close()
        return None  # No budget set for this month

    budget = budget_row[0]

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense' AND date LIKE ?", (f"{month}%",))
    total_expense = cursor.fetchone()[0] or 0.0
    conn.close()

    percent_used = (total_expense / budget) * 100 if budget > 0 else 0
    return {
        "budget": budget,
        "spent": total_expense,
        "remaining": budget - total_expense,
        "percent_used": percent_used,
        "is_exceeded": total_expense >= budget
    }

def get_transaction_by_id(transaction_id):
    """
    Fetch a single transaction by its ID to check for existence.
    Returns:
        A tuple with transaction data or None if not found.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM transactions WHERE id = ?", (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def delete_transaction_by_id(transaction_id):
    """
    Delete a transaction from the database using its ID.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

def update_transaction_by_id(transaction_id, new_type, new_category, new_amount):
    """
    Update the details of a specific transaction by its ID.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET type = ?, category = ?, amount = ?
        WHERE id = ?
    """, (new_type, new_category, new_amount, transaction_id))
    conn.commit()
    conn.close()
