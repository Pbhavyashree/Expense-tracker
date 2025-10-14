#!/usr/bin/env python3
"""
Test script to verify user registration and authentication functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_registration():
    """Test user registration"""
    print("Testing User Registration...")
    
    # Test data
    test_user = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }
    
    try:
        # Test registration
        response = requests.post(f"{BASE_URL}/register", data=test_user)
        print(f"Registration Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting User Login...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test login data
    login_data = {
        'username': 'testuser',
        'password': 'password123'
    }
    
    try:
        # Test login
        response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            
            # Test accessing dashboard (should work after login)
            dashboard_response = session.get(f"{BASE_URL}/")
            if dashboard_response.status_code == 200:
                print("✅ Dashboard access successful after login!")
                return True
            else:
                print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

def test_protected_route_without_login():
    """Test accessing protected route without login"""
    print("\nTesting Protected Route Access (without login)...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Dashboard Status Code (without login): {response.status_code}")
        
        if response.status_code == 302:  # Should redirect to login
            print("✅ Protected route correctly redirects to login!")
            return True
        else:
            print(f"❌ Protected route didn't redirect properly: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing protected route: {e}")
        return False

def main():
    """Run all tests"""
    print("🔄 Starting Authentication System Tests...\n")
    
    # Run tests
    tests = [
        ("Protected Route Test", test_protected_route_without_login),
        ("User Registration", test_registration),
        ("User Login", test_login),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All authentication tests passed! The system is working correctly.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the output above.")

if __name__ == "__main__":
    main()