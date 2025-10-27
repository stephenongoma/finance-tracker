import sqlite3

# Connect to the database
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Add a new column for type if it doesn't exist
try:
    cursor.execute("ALTER TABLE transactions ADD COLUMN type TEXT DEFAULT 'expense'")
    print("Database updated successfully!")
except sqlite3.OperationalError:
    print("Column 'type' already exists. Skipping update.")

conn.commit()
conn.close()
