from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, session, flash
import sqlite3
import os
from datetime import datetime, date
import csv
from io import StringIO
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'tracker.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create categories table (now per user)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(name, user_id)
        )
    ''')
    
    # Create transactions table (now per user)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            category_id INTEGER,
            description TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create budgets table (optional, now per user)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            category_id INTEGER,
            amount_limit REAL NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(month, category_id, user_id)
        )
    ''')
    
    # Create financial goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            target_amount REAL NOT NULL,
            target_date TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create recurring transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            category_id INTEGER,
            frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
            start_date TEXT NOT NULL,
            next_date TEXT NOT NULL,
            last_executed TEXT,
            description TEXT,
            user_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_default_categories(user_id):
    """Create default categories for a new user"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    default_categories = [
        ('Food & Dining', user_id), ('Transportation', user_id), ('Shopping', user_id),
        ('Entertainment', user_id), ('Bills & Utilities', user_id), ('Healthcare', user_id),
        ('Travel', user_id), ('Education', user_id), ('Salary', user_id), 
        ('Business', user_id), ('Other', user_id)
    ]
    
    try:
        cursor.executemany('INSERT INTO categories (name, user_id) VALUES (?, ?)', default_categories)
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Categories already exist for this user
    
    conn.close()

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = hash_password(password)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create default categories for new user
        create_default_categories(user_id)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, password_hash FROM users WHERE username = ? OR email = ?',
            (username, username)
        ).fetchone()
        conn.close()
        
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Dashboard page showing summary stats and recent transactions"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get total income, expense, and balance for current user
    income_result = conn.execute(
        'SELECT SUM(amount) FROM transactions WHERE type = "income" AND user_id = ?', 
        (user_id,)
    ).fetchone()
    expense_result = conn.execute(
        'SELECT SUM(amount) FROM transactions WHERE type = "expense" AND user_id = ?', 
        (user_id,)
    ).fetchone()
    
    total_income = income_result[0] if income_result[0] else 0
    total_expense = expense_result[0] if expense_result[0] else 0
    balance = total_income - total_expense
    
    # Get recent transactions (last 10) for current user
    recent_transactions = conn.execute('''
        SELECT t.*, c.name as category_name 
        FROM transactions t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.id DESC 
        LIMIT 10
    ''', (user_id,)).fetchall()
    
    # Get monthly data for chart for current user
    monthly_data = conn.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
        FROM transactions 
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 6
    ''', (user_id,)).fetchall()
    
    # Check for budget alerts (current month)
    current_month = datetime.now().strftime('%Y-%m')
    budget_alerts = []
    
    budgets = conn.execute('''
        SELECT b.*, c.name as category_name
        FROM budgets b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE b.user_id = ? AND b.month = ?
    ''', (user_id, current_month)).fetchall()
    
    for budget in budgets:
        spent = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions 
            WHERE user_id = ? AND type = 'expense' 
            AND category_id = ? 
            AND strftime('%Y-%m', date) = ?
        ''', (user_id, budget['category_id'], current_month)).fetchone()['total']
        
        percentage = (spent / budget['amount_limit']) * 100 if budget['amount_limit'] > 0 else 0
        
        if percentage >= 100:
            budget_alerts.append({
                'type': 'danger',
                'category': budget['category_name'],
                'message': f'Over budget by €{spent - budget["amount_limit"]:.2f}',
                'percentage': percentage
            })
        elif percentage >= 80:
            budget_alerts.append({
                'type': 'warning', 
                'category': budget['category_name'],
                'message': f'{percentage:.1f}% of budget used',
                'percentage': percentage
            })
    
    # Check for pending recurring transactions
    pending_recurring = conn.execute('''
        SELECT * FROM recurring_transactions 
        WHERE user_id = ? AND active = 1 
        AND next_date <= date('now')
        ORDER BY next_date ASC
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance,
                         recent_transactions=recent_transactions,
                         monthly_data=monthly_data,
                         budget_alerts=budget_alerts,
                         pending_recurring=pending_recurring)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add new transaction page"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        date_str = request.form['date']
        amount = float(request.form['amount'])
        transaction_type = request.form['type']
        category_id = int(request.form['category_id']) if request.form['category_id'] else None
        description = request.form['description']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO transactions (date, amount, type, category_id, description, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date_str, amount, transaction_type, category_id, description, user_id))
        conn.commit()
        conn.close()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show form with user's categories
    conn = get_db_connection()
    categories = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    conn.close()
    
    return render_template('add.html', categories=categories)

@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """Edit existing transaction"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        date_str = request.form['date']
        amount = float(request.form['amount'])
        transaction_type = request.form['type']
        category_id = int(request.form['category_id']) if request.form['category_id'] else None
        description = request.form['description']
        
        conn.execute('''
            UPDATE transactions 
            SET date = ?, amount = ?, type = ?, category_id = ?, description = ?
            WHERE id = ? AND user_id = ?
        ''', (date_str, amount, transaction_type, category_id, description, transaction_id, user_id))
        conn.commit()
        conn.close()
        
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show form with existing data (only if user owns the transaction)
    transaction = conn.execute(
        'SELECT * FROM transactions WHERE id = ? AND user_id = ?', 
        (transaction_id, user_id)
    ).fetchone()
    categories = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    conn.close()
    
    if not transaction:
        flash('Transaction not found.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('add.html', transaction=transaction, categories=categories, edit_mode=True)

@app.route('/delete/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    """Delete transaction"""
    user_id = session['user_id']
    conn = get_db_connection()
    result = conn.execute(
        'DELETE FROM transactions WHERE id = ? AND user_id = ?', 
        (transaction_id, user_id)
    )
    conn.commit()
    conn.close()
    
    if result.rowcount > 0:
        flash('Transaction deleted successfully!', 'success')
    else:
        flash('Transaction not found.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/categories')
@login_required
def categories():
    """Category management page"""
    user_id = session['user_id']
    conn = get_db_connection()
    categories_list = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    conn.close()
    
    return render_template('categories.html', categories=categories_list)

@app.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    """Add new category"""
    user_id = session['user_id']
    name = request.form['name'].strip()
    
    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('categories'))
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO categories (name, user_id) VALUES (?, ?)', 
            (name, user_id)
        )
        conn.commit()
        flash('Category added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Category already exists.', 'error')
    conn.close()
    
    return redirect(url_for('categories'))

@app.route('/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    """Delete category"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # First, update transactions to remove category reference (only for this user)
    conn.execute(
        'UPDATE transactions SET category_id = NULL WHERE category_id = ? AND user_id = ?', 
        (category_id, user_id)
    )
    # Then delete the category (only if it belongs to this user)
    result = conn.execute(
        'DELETE FROM categories WHERE id = ? AND user_id = ?', 
        (category_id, user_id)
    )
    conn.commit()
    conn.close()
    
    if result.rowcount > 0:
        flash('Category deleted successfully!', 'success')
    else:
        flash('Category not found.', 'error')
    
    return redirect(url_for('categories'))

@app.route('/reports')
@login_required
def reports():
    """Reports page with filtering options"""
    user_id = session['user_id']
    
    # Get filter parameters
    filter_type = request.args.get('type', '')
    filter_category = request.args.get('category', '')
    filter_month = request.args.get('month', '')
    filter_year = request.args.get('year', '')
    
    conn = get_db_connection()
    
    # Build query with filters (only for current user)
    query = '''
        SELECT t.*, c.name as category_name 
        FROM transactions t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    if filter_type:
        query += ' AND t.type = ?'
        params.append(filter_type)
    
    if filter_category:
        query += ' AND t.category_id = ?'
        params.append(filter_category)
    
    if filter_month:
        query += ' AND strftime("%m", t.date) = ?'
        params.append(filter_month.zfill(2))
    
    if filter_year:
        query += ' AND strftime("%Y", t.date) = ?'
        params.append(filter_year)
    
    query += ' ORDER BY t.date DESC, t.id DESC'
    
    transactions = conn.execute(query, params).fetchall()
    categories_list = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    
    # Get summary for filtered data (only for current user)
    summary_query = '''
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions t 
        WHERE t.user_id = ?
    '''
    summary_params = [user_id]
    
    if filter_type:
        summary_query += ' AND t.type = ?'
        summary_params.append(filter_type)
    if filter_category:
        summary_query += ' AND t.category_id = ?'
        summary_params.append(filter_category)
    if filter_month:
        summary_query += ' AND strftime("%m", t.date) = ?'
        summary_params.append(filter_month.zfill(2))
    if filter_year:
        summary_query += ' AND strftime("%Y", t.date) = ?'
        summary_params.append(filter_year)
    
    summary = conn.execute(summary_query, summary_params).fetchone()
    conn.close()
    
    return render_template('reports.html', 
                         transactions=transactions,
                         categories=categories_list,
                         filter_type=filter_type,
                         filter_category=filter_category,
                         filter_month=filter_month,
                         filter_year=filter_year,
                         total_income=summary['total_income'] or 0,
                         total_expense=summary['total_expense'] or 0)

@app.route('/budgets')
@login_required
def budgets():
    """Budget management page"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get current month
    current_month = datetime.now().strftime('%Y-%m')
    
    # Get all budgets for current user
    budgets = conn.execute('''
        SELECT b.*, c.name as category_name
        FROM budgets b 
        LEFT JOIN categories c ON b.category_id = c.id 
        WHERE b.user_id = ? 
        ORDER BY b.month DESC, c.name
    ''', (user_id,)).fetchall()
    
    # Get spending data for current month
    budget_status = []
    for budget in budgets:
        if budget['month'] == current_month:
            spent = conn.execute('''
                SELECT COALESCE(SUM(amount), 0) as total
                FROM transactions 
                WHERE user_id = ? AND type = 'expense' 
                AND category_id = ? 
                AND strftime('%Y-%m', date) = ?
            ''', (user_id, budget['category_id'], current_month)).fetchone()
            
            remaining = budget['amount_limit'] - spent['total']
            percentage = (spent['total'] / budget['amount_limit']) * 100 if budget['amount_limit'] > 0 else 0
            
            budget_status.append({
                'budget': budget,
                'spent': spent['total'],
                'remaining': remaining,
                'percentage': percentage,
                'over_budget': remaining < 0
            })
    
    # Get categories for dropdown
    categories = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('budgets.html', 
                         budgets=budgets,
                         budget_status=budget_status,
                         categories=categories,
                         current_month=current_month)

@app.route('/budgets/add', methods=['POST'])
@login_required
def add_budget():
    """Add new budget"""
    user_id = session['user_id']
    month = request.form['month']
    category_id = int(request.form['category_id'])
    amount_limit = float(request.form['amount_limit'])
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO budgets (month, category_id, amount_limit, user_id)
            VALUES (?, ?, ?, ?)
        ''', (month, category_id, amount_limit, user_id))
        conn.commit()
        flash('Budget added successfully!', 'success')
    except sqlite3.IntegrityError:
        # Update existing budget
        conn.execute('''
            UPDATE budgets 
            SET amount_limit = ? 
            WHERE month = ? AND category_id = ? AND user_id = ?
        ''', (amount_limit, month, category_id, user_id))
        conn.commit()
        flash('Budget updated successfully!', 'success')
    
    conn.close()
    return redirect(url_for('budgets'))

@app.route('/budgets/delete/<int:budget_id>')
@login_required
def delete_budget(budget_id):
    """Delete budget"""
    user_id = session['user_id']
    conn = get_db_connection()
    result = conn.execute(
        'DELETE FROM budgets WHERE id = ? AND user_id = ?', 
        (budget_id, user_id)
    )
    conn.commit()
    conn.close()
    
    if result.rowcount > 0:
        flash('Budget deleted successfully!', 'success')
    else:
        flash('Budget not found.', 'error')
    
    return redirect(url_for('budgets'))

@app.route('/analytics')
@login_required
def analytics():
    """Advanced analytics page"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get spending by category (last 6 months)
    category_spending = conn.execute('''
        SELECT c.name, SUM(t.amount) as total, COUNT(t.id) as count
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense' AND t.user_id = ?
        AND date >= date('now', '-6 months')
        GROUP BY c.id, c.name
        ORDER BY total DESC
        LIMIT 10
    ''', (user_id,)).fetchall()
    
    # Get monthly trends (last 12 months)
    monthly_trends = conn.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
        FROM transactions 
        WHERE user_id = ?
        AND date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 12
    ''', (user_id,)).fetchall()
    
    # Get top spending days
    top_spending_days = conn.execute('''
        SELECT date, SUM(amount) as daily_expense
        FROM transactions 
        WHERE type = 'expense' AND user_id = ?
        AND date >= date('now', '-3 months')
        GROUP BY date
        ORDER BY daily_expense DESC
        LIMIT 10
    ''', (user_id,)).fetchall()
    
    # Get average spending per category
    avg_spending = conn.execute('''
        SELECT 
            c.name,
            AVG(t.amount) as avg_amount,
            MIN(t.amount) as min_amount,
            MAX(t.amount) as max_amount
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense' AND t.user_id = ?
        GROUP BY c.id, c.name
        HAVING COUNT(t.id) >= 3
        ORDER BY avg_amount DESC
    ''', (user_id,)).fetchall()
    
    # Get savings rate (last 6 months)
    savings_data = conn.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
        FROM transactions 
        WHERE user_id = ?
        AND date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
    ''', (user_id,)).fetchall()
    
    # Calculate insights
    total_transactions = conn.execute(
        'SELECT COUNT(*) as count FROM transactions WHERE user_id = ?', 
        (user_id,)
    ).fetchone()['count']
    
    conn.close()
    
    # Calculate average savings rate
    avg_savings_rate = 0
    if savings_data:
        savings_rates = []
        for month_data in savings_data:
            if month_data['income'] > 0:
                savings = month_data['income'] - month_data['expense']
                rate = (savings / month_data['income']) * 100
                savings_rates.append(rate)
        
        if savings_rates:
            avg_savings_rate = sum(savings_rates) / len(savings_rates)
    
    return render_template('analytics.html',
                         category_spending=category_spending,
                         monthly_trends=monthly_trends,
                         top_spending_days=top_spending_days,
                         avg_spending=avg_spending,
                         savings_data=savings_data,
                         avg_savings_rate=avg_savings_rate,
                         total_transactions=total_transactions)

@app.route('/search')
@login_required
def search():
    """Search transactions"""
    user_id = session['user_id']
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', transactions=[], query='')
    
    conn = get_db_connection()
    
    # Search in description and category names
    transactions = conn.execute('''
        SELECT t.*, c.name as category_name 
        FROM transactions t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ? AND (
            t.description LIKE ? OR 
            c.name LIKE ? OR
            t.amount LIKE ? OR
            t.date LIKE ?
        )
        ORDER BY t.date DESC, t.id DESC
        LIMIT 100
    ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    
    conn.close()
    
    return render_template('search.html', transactions=transactions, query=query)

@app.route('/recurring')
@login_required  
def recurring_transactions():
    """Manage recurring transactions"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all recurring transactions for current user
    recurring = conn.execute('''
        SELECT r.*, c.name as category_name
        FROM recurring_transactions r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = ?
        ORDER BY r.next_date ASC
    ''', (user_id,)).fetchall()
    
    # Get categories for form
    categories = conn.execute(
        'SELECT * FROM categories WHERE user_id = ? ORDER BY name', 
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    return render_template('recurring.html', recurring=recurring, categories=categories)

@app.route('/recurring/add', methods=['POST'])
@login_required
def add_recurring_transaction():
    """Add new recurring transaction"""
    user_id = session['user_id']
    
    title = request.form['title']
    amount = float(request.form['amount'])
    transaction_type = request.form['type']
    category_id = int(request.form['category_id']) if request.form['category_id'] else None
    frequency = request.form['frequency']  # daily, weekly, monthly, yearly
    start_date = request.form['start_date']
    description = request.form['description']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO recurring_transactions 
        (title, amount, type, category_id, frequency, start_date, next_date, description, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, amount, transaction_type, category_id, frequency, start_date, start_date, description, user_id))
    conn.commit()
    conn.close()
    
    flash('Recurring transaction added successfully!', 'success')
    return redirect(url_for('recurring_transactions'))

@app.route('/recurring/execute/<int:recurring_id>')
@login_required
def execute_recurring_transaction(recurring_id):
    """Execute a recurring transaction"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get the recurring transaction
    recurring = conn.execute('''
        SELECT * FROM recurring_transactions 
        WHERE id = ? AND user_id = ?
    ''', (recurring_id, user_id)).fetchone()
    
    if not recurring:
        flash('Recurring transaction not found.', 'error')
        return redirect(url_for('recurring_transactions'))
    
    # Create the actual transaction
    conn.execute('''
        INSERT INTO transactions (date, amount, type, category_id, description, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (recurring['next_date'], recurring['amount'], recurring['type'], 
          recurring['category_id'], f"{recurring['title']} (Auto)", user_id))
    
    # Calculate next date based on frequency
    from datetime import datetime, timedelta
    next_date = datetime.strptime(recurring['next_date'], '%Y-%m-%d')
    
    if recurring['frequency'] == 'daily':
        next_date += timedelta(days=1)
    elif recurring['frequency'] == 'weekly':
        next_date += timedelta(weeks=1)
    elif recurring['frequency'] == 'monthly':
        if next_date.month == 12:
            next_date = next_date.replace(year=next_date.year + 1, month=1)
        else:
            next_date = next_date.replace(month=next_date.month + 1)
    elif recurring['frequency'] == 'yearly':
        next_date = next_date.replace(year=next_date.year + 1)
    
    # Update next date
    conn.execute('''
        UPDATE recurring_transactions 
        SET next_date = ?, last_executed = ?
        WHERE id = ? AND user_id = ?
    ''', (next_date.strftime('%Y-%m-%d'), recurring['next_date'], recurring_id, user_id))
    
    conn.commit()
    conn.close()
    
    flash(f'Recurring transaction "{recurring["title"]}" executed successfully!', 'success')
    return redirect(url_for('recurring_transactions'))

@app.route('/goals')
@login_required
def goals():
    """Financial goals tracking"""
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Get all goals for current user
    goals = conn.execute('''
        SELECT * FROM financial_goals 
        WHERE user_id = ? 
        ORDER BY target_date ASC
    ''', (user_id,)).fetchall()
    
    # Calculate progress for each goal
    goals_with_progress = []
    for goal in goals:
        current_amount = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions 
            WHERE user_id = ? AND type = 'income' 
            AND description LIKE ? 
            AND date >= ?
        ''', (user_id, f'%{goal["title"]}%', goal['created_at'])).fetchone()['total']
        
        progress_percentage = (current_amount / goal['target_amount']) * 100 if goal['target_amount'] > 0 else 0
        days_left = (datetime.strptime(goal['target_date'], '%Y-%m-%d') - datetime.now()).days
        
        goals_with_progress.append({
            'goal': goal,
            'current_amount': current_amount,
            'progress_percentage': min(progress_percentage, 100),
            'days_left': max(days_left, 0),
            'completed': current_amount >= goal['target_amount']
        })
    
    conn.close()
    
    return render_template('goals.html', goals=goals_with_progress)

@app.route('/export')
@login_required
def export_csv():
    """Export transactions as CSV"""
    user_id = session['user_id']
    
    # Get same filters as reports
    filter_type = request.args.get('type', '')
    filter_category = request.args.get('category', '')
    filter_month = request.args.get('month', '')
    filter_year = request.args.get('year', '')
    
    conn = get_db_connection()
    
    # Build query with filters (only for current user)
    query = '''
        SELECT t.date, t.amount, t.type, c.name as category_name, t.description 
        FROM transactions t 
        LEFT JOIN categories c ON t.category_id = c.id 
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    if filter_type:
        query += ' AND t.type = ?'
        params.append(filter_type)
    
    if filter_category:
        query += ' AND t.category_id = ?'
        params.append(filter_category)
    
    if filter_month:
        query += ' AND strftime("%m", t.date) = ?'
        params.append(filter_month.zfill(2))
    
    if filter_year:
        query += ' AND strftime("%Y", t.date) = ?'
        params.append(filter_year)
    
    query += ' ORDER BY t.date DESC'
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Amount', 'Type', 'Category', 'Description'])
    
    for transaction in transactions:
        writer.writerow([
            transaction['date'],
            transaction['amount'],
            transaction['type'],
            transaction['category_name'] or 'No Category',
            transaction['description'] or ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
    
    return response

@app.route('/about')
def about():
    """About page with application information"""
    return render_template('about.html')

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(debug=True)