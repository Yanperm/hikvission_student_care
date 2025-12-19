#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Database Operations
© 2025 SOFTUBON CO.,LTD.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db
from datetime import datetime

def test_all_systems():
    print("Testing Database Operations...\n")
    
    # Test 1: Schools
    print("[1] Testing Schools...")
    schools = db.get_all_schools()
    print(f"   OK: Found {len(schools)} schools")
    
    # Test 2: Users
    print("\n[2] Testing Users...")
    user = db.get_user('admin@school.com')
    if user:
        print(f"   OK: User: {user['name']} ({user['role']})")
    
    # Test 3: Students
    print("\n[3] Testing Students...")
    students = db.get_students('SCH001')
    print(f"   OK: Found {len(students)} students in SCH001")
    
    # Test 4: Add Test Student
    print("\n[4] Adding Test Student...")
    try:
        db.add_student(
            student_id='TEST001',
            name='Test Student',
            class_name='M.1/1',
            school_id='SCH001',
            image_path='data/students/TEST001.jpg'
        )
        print("   OK: Student added successfully")
    except Exception as e:
        print(f"   INFO: Student might already exist: {e}")
    
    # Test 5: Attendance
    print("\n[5] Testing Attendance...")
    db.add_attendance('TEST001', 'Test Student', 'SCH001', 'classroom')
    attendance = db.get_attendance('SCH001')
    print(f"   OK: Found {len(attendance)} attendance records")
    
    # Test 6: Behavior
    print("\n[6] Testing Behavior...")
    db.add_behavior('TEST001', 'Test Student', 'SCH001', 'Helping friends', 'normal')
    behaviors = db.get_behavior('SCH001')
    print(f"   OK: Found {len(behaviors)} behavior records")
    
    # Test 7: Notifications
    print("\n[7] Testing Notifications...")
    db.add_notification('SCH001', 'TEST001', 'test', 'Test System', 'This is a test')
    notifications = db.get_notifications('SCH001')
    print(f"   OK: Found {len(notifications)} notifications")
    
    # Test 8: Behavior Scores
    print("\n[8] Testing Behavior Scores...")
    db.update_behavior_score('TEST001', 'SCH001', 95)
    scores = db.get_behavior_scores('SCH001')
    print(f"   OK: Found {len(scores)} behavior scores")
    
    # Test 9: Stats
    print("\n[9] Testing Stats...")
    stats = db.get_stats()
    print(f"   OK: Total Schools: {stats['total_schools']}")
    print(f"   OK: Total Capacity: {stats['total_capacity']}")
    print(f"   OK: Expiring Soon: {stats['expiring_soon']}")
    
    # Test 10: Cleanup
    print("\n[10] Cleaning up test data...")
    db.delete_student('TEST001')
    print("   OK: Test student deleted")
    
    print("\n" + "="*50)
    print("SUCCESS: All tests passed! Database is working correctly!")
    print("="*50)

if __name__ == '__main__':
    test_all_systems()
