# 💰 Personal Finance Tracker (Python + SQLite)

A simple **command-line personal finance tracker** built with Python and SQLite.  
It helps you record your **income** and **expenses**, view **summaries**, and track **spending by category** — all from your terminal.

---

## 🧩 Features

- 🧾 Add income and expense transactions  
- 💼 Categorize spending (e.g. Food, Transport, Bills)  
- 📊 View total income, expenses, and balance  
- 📂 View expenses grouped by category  
- 💾 Stores data locally using **SQLite** (in `data/finance.db`)  
- 🧱 Clean, modular design for easy upgrades

---

## ⚙️ Requirements

- **Python 3.8+**
- No external dependencies — uses only Python's built-in libraries.

---

## 🗂️ Project Structure


finance-tracker/
├── database.py # Handles all database operations
├── finance_tracker.py # Main program (CLI menu)
├── data/
│ └── finance.db # SQLite database (auto-created)
└── README.md

---

## 🚀 How to Run

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/stephenongoma/finance-tracker.git
   cd finance-tracker

2. Run the program: 
python finance_tracker.py

3. Use the menu options:
💰 PERSONAL FINANCE TRACKER
==============================
1. Add Income
2. Add Expense
3. View Summary
4. View Expenses by Category
5. Exit

4. Your data will be saved automatically in data/finance.db.
Enter your choice (1-5): 1
Enter income category (e.g., Salary, Bonus): Salary
Enter amount: 1500
✅ Income of 1500.00 added under 'Salary'.

Enter your choice (1-5): 2
Enter expense category (e.g., Food, Transport): Food
Enter amount: 300
✅ Expense of 300.00 added under 'Food'.

Enter your choice (1-5): 3
📊 FINANCIAL SUMMARY
------------------------------
Total Income   : 1500.00
Total Expenses : 300.00
Current Balance: 1200.00
------------------------------

🧱 Future Enhancements

📆 View all transactions by date

📈 Add charts using matplotlib

💬 Budget alerts and monthly limits

🌐 Web dashboard version

👨‍💻 Author

Stephen Ongoma
📍 Dedan Kimathi University of Technology
📘 Personal project for learning and GitHub portfolio
🔗 GitHub: stephenongoma

🪪 License

This project is open-source and available under the MIT License.

