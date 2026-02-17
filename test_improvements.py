#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Script for Improved System
"""

import sys
import os

def test_imports():
    print("🧪 Testing imports...")
    try:
        from security.password_manager import password_manager
        from security.csrf_protection import csrf
        from security.rate_limiter import limiter
        from utils.cache import cache
        from utils.validator import validator
        from database_improved import db
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_password_hashing():
    print("\n🔐 Testing password hashing...")
    try:
        from security.password_manager import password_manager
        
        password = "test123"
        hashed = password_manager.hash_password(password)
        
        assert hashed != password, "Password not hashed"
        assert password_manager.verify_password(password, hashed), "Verification failed"
        assert not password_manager.verify_password("wrong", hashed), "Wrong password verified"
        
        print("✅ Password hashing works")
        return True
    except Exception as e:
        print(f"❌ Password hashing failed: {e}")
        return False

def test_validator():
    print("\n✅ Testing validator...")
    try:
        from utils.validator import validator
        
        # Test student ID
        valid, msg = validator.validate_student_id("STD001")
        assert valid, "Valid student ID rejected"
        
        valid, msg = validator.validate_student_id("AB")
        assert not valid, "Invalid student ID accepted"
        
        # Test email
        valid, msg = validator.validate_email("test@example.com")
        assert valid, "Valid email rejected"
        
        valid, msg = validator.validate_email("invalid")
        assert not valid, "Invalid email accepted"
        
        print("✅ Validator works")
        return True
    except Exception as e:
        print(f"❌ Validator failed: {e}")
        return False

def test_cache():
    print("\n💾 Testing cache...")
    try:
        from utils.cache import cache
        
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        assert value == "test_value", "Cache get/set failed"
        
        cache.delete("test_key")
        value = cache.get("test_key")
        assert value is None, "Cache delete failed"
        
        print("✅ Cache works")
        return True
    except Exception as e:
        print(f"❌ Cache failed: {e}")
        return False

def test_database():
    print("\n🗄️ Testing database...")
    try:
        from database_improved import db
        
        # Test connection
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count > 0, "No users in database"
        
        # Test get_user
        user = db.get_user("superadmin")
        assert user is not None, "User not found"
        assert 'password' in user, "Password field missing"
        
        print(f"✅ Database works ({count} users)")
        return True
    except Exception as e:
        print(f"❌ Database failed: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 IMPROVED SYSTEM TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_password_hashing,
        test_validator,
        test_cache,
        test_database
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed! System is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
