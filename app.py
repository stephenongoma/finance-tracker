"""
Finance Tracker - Flask Web Application
Web interface for managing personal finances
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
from database import (
    create_table,
    create_budget_table,
    add_transaction,
    get_summary,
    get_expenses_by_category,
    get_all_transactions,
    set_monthly_budget,
    check_monthly_budget,
    get_transaction_by_id,
    delete_transaction_by_id,
    update_transaction_by_id,
)
from database import connect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Initialize database on startup
create_table()
create_budget_table()


@app.route('/')
def index():
    """Dashboard home page."""
    total_income, total_expense, balance = get_summary()
    budget_status = check_monthly_budget()
    expenses_by_category = get_expenses_by_category()
    recent_transactions = get_all_transactions()[:5]  # Get last 5 transactions
    
    return render_template('dashboard.html',
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance,
                         budget_status=budget_status,
                         expenses_by_category=expenses_by_category,
                         recent_transactions=recent_transactions)


@app.route('/api/add-transaction', methods=['POST'])
def api_add_transaction():
    """API endpoint to add a transaction."""
    try:
        data = request.get_json()
        trans_type = data.get('type', '').lower()
        category = data.get('category', '').strip()
        amount = float(data.get('amount', 0))
        
        if trans_type not in ['income', 'expense']:
            return jsonify({'success': False, 'message': 'Invalid transaction type'}), 400
        
        if not category:
            return jsonify({'success': False, 'message': 'Category is required'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400
        
        add_transaction(trans_type, category, amount)
        return jsonify({'success': True, 'message': f'{trans_type.capitalize()} added successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/summary')
def api_summary():
    """API endpoint to get financial summary."""
    try:
        total_income, total_expense, balance = get_summary()
        budget_status = check_monthly_budget()
        
        return jsonify({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'budget_status': budget_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions')
def api_transactions():
    """API endpoint to get all transactions."""
    try:
        transactions = get_all_transactions()
        trans_list = [{
            'id': t[0],
            'date': t[1],
            'category': t[2],
            'amount': t[3],
            'type': t[4]
        } for t in transactions]
        return jsonify(trans_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/expenses-by-category')
def api_expenses_by_category():
    """API endpoint to get expenses grouped by category."""
    try:
        expenses = get_expenses_by_category()
        expense_list = [{
            'category': cat,
            'amount': amount
        } for cat, amount in expenses]
        return jsonify(expense_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monthly-summary')
def api_monthly_summary():
    """Return monthly totals for income and expense for the last 12 months."""
    try:
        conn = connect()
        cursor = conn.cursor()
        # Group by year-month
        cursor.execute("""
            SELECT substr(date,1,7) as month,
                   SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        rows = cursor.fetchall()
        conn.close()

        # Return data in chronological order (oldest first)
        rows = list(reversed(rows))
        result = [{'month': r[0], 'income': r[1] or 0, 'expense': r[2] or 0} for r in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/category-distribution')
def api_category_distribution():
    """Return expense totals per category for the current month."""
    try:
        from datetime import datetime
        month = datetime.now().strftime("%Y-%m")
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE type='expense' AND substr(date,1,7)=?
            GROUP BY category
            ORDER BY total DESC
        """, (month,))
        rows = cursor.fetchall()
        conn.close()

        result = [{'category': r[0], 'amount': r[1] or 0} for r in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set-budget', methods=['POST'])
def api_set_budget():
    """API endpoint to set monthly budget."""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Budget must be greater than 0'}), 400
        
        month = datetime.now().strftime("%Y-%m")
        set_monthly_budget(month, amount)
        return jsonify({'success': True, 'message': f'Budget set for {month}: Ksh {amount:,.2f}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete-transaction/<int:trans_id>', methods=['DELETE'])
def api_delete_transaction(trans_id):
    """API endpoint to delete a transaction."""
    try:
        if not get_transaction_by_id(trans_id):
            return jsonify({'success': False, 'message': 'Transaction not found'}), 404
        
        delete_transaction_by_id(trans_id)
        return jsonify({'success': True, 'message': 'Transaction deleted successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/update-transaction/<int:trans_id>', methods=['PUT'])
def api_update_transaction(trans_id):
    """API endpoint to update a transaction."""
    try:
        if not get_transaction_by_id(trans_id):
            return jsonify({'success': False, 'message': 'Transaction not found'}), 404
        
        data = request.get_json()
        new_type = data.get('type', '').lower()
        new_category = data.get('category', '').strip()
        new_amount = float(data.get('amount', 0))
        
        if new_type not in ['income', 'expense']:
            return jsonify({'success': False, 'message': 'Invalid transaction type'}), 400
        
        if not new_category:
            return jsonify({'success': False, 'message': 'Category is required'}), 400
        
        if new_amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400
        
        update_transaction_by_id(trans_id, new_type, new_category, new_amount)
        return jsonify({'success': True, 'message': 'Transaction updated successfully!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/transactions')
def transactions():
    """View all transactions page."""
    all_transactions = get_all_transactions()
    return render_template('transactions.html', transactions=all_transactions)


@app.route('/add')
def add_page():
    """Add transaction page."""
    return render_template('add_transaction.html')


@app.route('/budget')
def budget():
    """Budget management page."""
    budget_status = check_monthly_budget()
    return render_template('budget.html', budget_status=budget_status)


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Run the Flask app in debug mode (change to False in production)
    app.run(debug=True, host='0.0.0.0', port=5000)
