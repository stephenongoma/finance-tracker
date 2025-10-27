import sqlite3

# Connect to the database
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Create a table to store the user's monthly budget
cursor.execute("""
CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    amount REAL
)
""")

conn.commit()
conn.close()

print("✅ Budget table checked/created successfully!")
