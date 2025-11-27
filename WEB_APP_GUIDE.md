# 🚀 Running the Finance Tracker Web App

## Setup Instructions

### 1. Install Flask
```bash
pip install flask
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 3. Access the Web App
Open your browser and go to:
```
http://localhost:5000
```

## Features

### Dashboard (`/`)
- View your financial summary (total income, expenses, balance)
- See current month's budget status
- View expenses by category
- See recent transactions

### Add Transaction (`/add`)
- Add new income or expense transactions
- Select category and amount
- Transactions are saved to the database

### View Transactions (`/transactions`)
- See all transactions in a table format
- Edit existing transactions
- Delete transactions
- Filter and search capabilities

### Budget Management (`/budget`)
- Set monthly budget
- Monitor spending against budget
- See budget remaining or overage
- Visual progress indicator

## API Endpoints

- `GET /api/summary` - Get financial summary
- `POST /api/add-transaction` - Add new transaction
- `GET /api/transactions` - Get all transactions
- `GET /api/expenses-by-category` - Get expenses grouped by category
- `POST /api/set-budget` - Set monthly budget
- `PUT /api/update-transaction/<id>` - Update a transaction
- `DELETE /api/delete-transaction/<id>` - Delete a transaction

## Project Structure

```
finance-tracker/
├── app.py                    # Flask application
├── database.py              # Database operations
├── finance_tracker.py       # CLI version (still available)
├── analysis.py              # Analytics module
├── report_generator.py      # PDF report generator
├── requirements.txt         # Python dependencies
├── data/
│   └── finance.db          # SQLite database
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── dashboard.html      # Dashboard page
│   ├── add_transaction.html # Add transaction page
│   ├── transactions.html   # View transactions page
│   ├── budget.html         # Budget management page
│   ├── 404.html            # 404 error page
│   └── 500.html            # 500 error page
└── static/                 # Static files
    ├── css/
    │   └── style.css       # Main stylesheet
    └── js/
        └── main.js         # JavaScript utilities
```

## Development Notes

- The app runs in **debug mode** by default. For production, change `debug=True` to `debug=False` in `app.py`
- Database is stored in `data/finance.db`
- All existing CLI functionality is preserved in `finance_tracker.py`
- You can use both the web app and CLI at the same time - they share the same database

## Troubleshooting

### Port Already in Use
If port 5000 is busy, modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001
```

### Missing Dependencies
Ensure all packages are installed:
```bash
pip install -r requirements.txt
```

### Database Issues
If you encounter database errors, the app will automatically create tables on startup.

## Next Steps

- Add data visualization charts to the dashboard
- Implement CSV/Excel export functionality
- Add spending prediction based on history
- Create expense reports
- Add user authentication for multi-user support
