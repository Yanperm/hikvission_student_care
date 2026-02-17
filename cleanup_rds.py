#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

print("=" * 60)
print("RDS Connection Cleanup")
print("=" * 60)

try:
    import psycopg2
    
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME', 'postgres'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT', '5432')
    )
    
    cursor = conn.cursor()
    
    # Show current connections
    cursor.execute("""
        SELECT pid, usename, application_name, client_addr, state, query_start
        FROM pg_stat_activity
        WHERE datname = %s AND usename = %s
    """, (os.environ.get('DB_NAME', 'postgres'), os.environ.get('DB_USER')))
    
    connections = cursor.fetchall()
    print(f"\nActive connections: {len(connections)}")
    
    for conn_info in connections:
        print(f"  PID: {conn_info[0]}, State: {conn_info[4]}")
    
    # Terminate idle connections
    cursor.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s 
        AND usename = %s
        AND pid <> pg_backend_pid()
        AND state = 'idle'
    """, (os.environ.get('DB_NAME', 'postgres'), os.environ.get('DB_USER')))
    
    terminated = cursor.rowcount
    conn.commit()
    
    print(f"\nTerminated {terminated} idle connections")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nNote: This is normal if you don't have superuser privileges")
    print("Contact AWS RDS admin to increase max_connections")
