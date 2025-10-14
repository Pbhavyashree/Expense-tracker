"""
Sample data script for the Expense Tracker
Run this script to add some sample transactions for testing
"""

import sqlite3
import os
from datetime import datetime, timedelta

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'tracker.db')

def add_sample_data():
    """Add sample transactions to the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get category IDs
    categories = {
        'Food & Dining': 1,
        'Transportation': 2,
        'Shopping': 3,
        'Entertainment': 4,
        'Bills & Utilities': 5,
        'Healthcare': 6,
        'Travel': 7,
        'Education': 8,
        'Salary': 9,
        'Business': 10,
        'Other': 11
    }
    
    # Sample transactions
    sample_transactions = [
        # Income
        ('2025-09-01', 5000.00, 'income', categories['Salary'], 'Monthly salary'),
        ('2025-09-15', 1200.00, 'income', categories['Business'], 'Freelance project'),
        ('2025-08-01', 5000.00, 'income', categories['Salary'], 'Monthly salary'),
        ('2025-08-10', 800.00, 'income', categories['Business'], 'Consulting work'),
        
        # Expenses
        ('2025-09-25', 85.50, 'expense', categories['Food & Dining'], 'Grocery shopping'),
        ('2025-09-24', 12.75, 'expense', categories['Transportation'], 'Bus fare'),
        ('2025-09-23', 299.99, 'expense', categories['Shopping'], 'New headphones'),
        ('2025-09-22', 45.00, 'expense', categories['Entertainment'], 'Movie tickets'),
        ('2025-09-21', 125.80, 'expense', categories['Bills & Utilities'], 'Electric bill'),
        ('2025-09-20', 75.00, 'expense', categories['Healthcare'], 'Doctor visit'),
        ('2025-09-19', 32.50, 'expense', categories['Food & Dining'], 'Lunch with friends'),
        ('2025-09-18', 150.00, 'expense', categories['Shopping'], 'Clothing'),
        ('2025-09-17', 25.00, 'expense', categories['Transportation'], 'Uber ride'),
        ('2025-09-16', 89.99, 'expense', categories['Entertainment'], 'Gaming subscription'),
        ('2025-09-15', 200.00, 'expense', categories['Travel'], 'Weekend trip'),
        
        # August expenses
        ('2025-08-30', 95.25, 'expense', categories['Food & Dining'], 'Weekly groceries'),
        ('2025-08-28', 45.00, 'expense', categories['Transportation'], 'Gas'),
        ('2025-08-25', 120.00, 'expense', categories['Bills & Utilities'], 'Internet bill'),
        ('2025-08-22', 67.80, 'expense', categories['Food & Dining'], 'Restaurant dinner'),
        ('2025-08-20', 35.99, 'expense', categories['Entertainment'], 'Streaming service'),
        ('2025-08-18', 180.00, 'expense', categories['Healthcare'], 'Dental checkup'),
        ('2025-08-15', 55.50, 'expense', categories['Shopping'], 'Home supplies'),
        ('2025-08-12', 89.00, 'expense', categories['Food & Dining'], 'Coffee shop visits'),
        ('2025-08-10', 250.00, 'expense', categories['Education'], 'Online course'),
        ('2025-08-08', 75.25, 'expense', categories['Transportation'], 'Public transport pass'),
    ]
    
    # Insert sample transactions
    for transaction in sample_transactions:
        cursor.execute('''
            INSERT INTO transactions (date, amount, type, category_id, description)
            VALUES (?, ?, ?, ?, ?)
        ''', transaction)
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data added successfully!")
    print(f"📊 Added {len(sample_transactions)} sample transactions")
    print("🌐 Visit http://localhost:5000 to see the data")

if __name__ == '__main__':
    add_sample_data()