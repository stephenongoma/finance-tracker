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
