"""
Test script to verify user authentication is working correctly
"""

import sqlite3
import os
import hashlib

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'tracker.db')

def test_user_system():
    """Test the user authentication system"""
    print("🧪 Testing user authentication system...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if users table exists and has correct structure
    cursor.execute('''
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='users'
    ''')
    
    users_table = cursor.fetchone()
    if users_table:
        print("✅ Users table exists with structure:")
        print(f"   {users_table['sql']}")
    else:
        print("❌ Users table not found!")
        return
    
    # Check current users
    cursor.execute('SELECT id, username, email FROM users')
    users = cursor.fetchall()
    
    print(f"\n👥 Current users in system: {len(users)}")
    for user in users:
        print(f"   - {user['username']} ({user['email']})")
    
    # Check transactions per user
    cursor.execute('''
        SELECT u.username, COUNT(t.id) as transaction_count
        FROM users u
        LEFT JOIN transactions t ON u.id = t.user_id
        GROUP BY u.id, u.username
    ''')
    
    user_stats = cursor.fetchall()
    print(f"\n📊 Transaction counts per user:")
    for stat in user_stats:
        print(f"   - {stat['username']}: {stat['transaction_count']} transactions")
    
    # Check categories per user
    cursor.execute('''
        SELECT u.username, COUNT(c.id) as category_count
        FROM users u
        LEFT JOIN categories c ON u.id = c.user_id
        GROUP BY u.id, u.username
    ''')
    
    category_stats = cursor.fetchall()
    print(f"\n🏷️ Category counts per user:")
    for stat in category_stats:
        print(f"   - {stat['username']}: {stat['category_count']} categories")
    
    conn.close()
    print("\n✅ User system test completed!")

if __name__ == '__main__':
    test_user_system()