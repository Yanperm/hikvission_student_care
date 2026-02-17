#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

print("=" * 60)
print("RDS Connection Test")
print("=" * 60)

# Check environment variables
print("\n📋 Configuration:")
print(f"DB_TYPE: {os.environ.get('DB_TYPE', 'Not set')}")
print(f"USE_POSTGRES: {os.environ.get('USE_POSTGRES', 'Not set')}")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'Not set')}")
print(f"DB_NAME: {os.environ.get('DB_NAME', 'Not set')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'Not set')}")
print(f"DB_PORT: {os.environ.get('DB_PORT', 'Not set')}")

# Test connection
print("\n🔌 Testing connection...")
try:
    from database_universal import db
    
    print(f"✅ Database type: {db.db_type}")
    
    # Test query
    conn = db.get_connection()
    cursor = conn.cursor()
    
    if db.db_type == 'postgresql':
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL version: {version[:50]}...")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"✅ Students in database: {student_count}")
        
        cursor.execute("SELECT COUNT(*) FROM schools")
        school_count = cursor.fetchone()[0]
        print(f"✅ Schools in database: {school_count}")
    else:
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"✅ SQLite version: {version}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Connection successful!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Check .env file exists")
    print("2. Verify DB_HOST, DB_USER, DB_PASSWORD")
    print("3. Check RDS security group allows your IP")
    print("4. Install: pip install psycopg2-binary")
