"""
Database Migration Script
This script migrates the existing expense tracker database to support multiple users.
Run this script after implementing user authentication.
"""

import sqlite3
import os
from datetime import datetime

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'tracker.db')

def migrate_database():
    """Migrate existing database to support users"""
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        ''')
        
        if cursor.fetchone():
            print("✅ Database already migrated!")
            return
        
        print("📝 Creating backup of current data...")
        
        # Backup existing data
        cursor.execute('SELECT * FROM transactions')
        old_transactions = cursor.fetchall()
        
        cursor.execute('SELECT * FROM categories')
        old_categories = cursor.fetchall()
        
        print(f"📊 Found {len(old_transactions)} transactions and {len(old_categories)} categories")
        
        # Drop existing tables
        print("🗑️ Dropping old tables...")
        cursor.execute('DROP TABLE IF EXISTS transactions')
        cursor.execute('DROP TABLE IF EXISTS categories')
        cursor.execute('DROP TABLE IF EXISTS budgets')
        
        # Create new schema with users
        print("🏗️ Creating new schema...")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create categories table (now per user)
        cursor.execute('''
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(name, user_id)
            )
        ''')
        
        # Create transactions table (now per user)
        cursor.execute('''
            CREATE TABLE transactions (
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
            CREATE TABLE budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category_id INTEGER,
                amount_limit REAL NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create a default demo user for existing data
        print("👤 Creating demo user for existing data...")
        import hashlib
        demo_password = hashlib.sha256("demo123".encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash) 
            VALUES (?, ?, ?)
        ''', ("demo", "demo@example.com", demo_password))
        
        demo_user_id = cursor.lastrowid
        
        # Migrate categories
        print("🏷️ Migrating categories...")
        category_mapping = {}
        
        for old_cat in old_categories:
            cursor.execute('''
                INSERT INTO categories (name, user_id) 
                VALUES (?, ?)
            ''', (old_cat[1], demo_user_id))  # old_cat[1] is the name
            
            new_cat_id = cursor.lastrowid
            category_mapping[old_cat[0]] = new_cat_id  # Map old ID to new ID
        
        # Migrate transactions
        print("💰 Migrating transactions...")
        for old_trans in old_transactions:
            old_category_id = old_trans[4]  # category_id position
            new_category_id = category_mapping.get(old_category_id) if old_category_id else None
            
            cursor.execute('''
                INSERT INTO transactions (date, amount, type, category_id, description, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                old_trans[1],  # date
                old_trans[2],  # amount  
                old_trans[3],  # type
                new_category_id,  # new category_id
                old_trans[5],  # description
                demo_user_id   # user_id
            ))
        
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print(f"👤 Demo user created:")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Email: demo@example.com")
        print(f"📊 Migrated {len(old_transactions)} transactions and {len(old_categories)} categories")
        print(f"🌐 You can now register new users or login with the demo account")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()