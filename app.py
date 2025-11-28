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


@app.route('/csv')
def csv_page():
    """CSV import/export page."""
    return render_template('csv.html')


@app.route('/api/export-csv')
def api_export_csv():
    """Export all transactions to CSV format."""
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        transactions = get_all_transactions()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Date', 'Category', 'Amount', 'Type'])
        for trans_id, date, category, amount, trans_type in transactions:
            writer.writerow([trans_id, date, category, amount, trans_type])
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=transactions_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/import-csv', methods=['POST'])
def api_import_csv():
    """Import transactions from uploaded CSV file."""
    try:
        import csv
        from io import TextIOWrapper
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'message': 'File must be a CSV'}), 400
        
        stream = TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(stream)
        
        transactions_to_add = []
        skipped = 0
        
        for row_num, row in enumerate(reader, start=2):
            try:
                trans_type = row.get('type', '').lower().strip()
                category = row.get('category', '').strip()
                amount = float(row.get('amount', 0))
                date_str = row.get('date', '').strip()
                
                if trans_type not in ['income', 'expense']:
                    skipped += 1
                    continue
                
                if not category or amount <= 0:
                    skipped += 1
                    continue
                
                if date_str:
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                            date_str = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                transactions_to_add.append((trans_type, category, amount, date_str))
            except Exception as e:
                skipped += 1
                continue
        
        if transactions_to_add:
            from database import add_bulk_transactions
            add_bulk_transactions(transactions_to_add)
            message = f'Successfully imported {len(transactions_to_add)} transactions.'
            if skipped > 0:
                message += f' ({skipped} rows skipped due to errors).'
            return jsonify({'success': True, 'message': message, 'imported': len(transactions_to_add)})
        else:
            return jsonify({'success': False, 'message': f'No valid transactions found to import. {skipped} rows skipped.'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing CSV: {str(e)}'}), 500


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
