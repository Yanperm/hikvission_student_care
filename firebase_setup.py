"""
Firebase Setup for Student Care System
Run this script to initialize Firebase Firestore database
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

def setup_firebase():
    """Initialize Firebase and create initial collections"""
    
    print("🔥 Setting up Firebase Firestore...")
    
    try:
        # Initialize Firebase (using default credentials in Cloud Run)
        if not firebase_admin._apps:
            # For local development, use service account key
            # cred = credentials.Certificate("path/to/serviceAccountKey.json")
            # firebase_admin.initialize_app(cred)
            
            # For Cloud Run, use default credentials
            firebase_admin.initialize_app()
        
        db = firestore.client()
        
        # Create initial collections and documents
        print("📚 Creating initial collections...")
        
        # Create system settings
        system_ref = db.collection('system').document('settings')
        system_ref.set({
            'app_name': 'Student Care System',
            'version': '1.0.0',
            'created_at': datetime.now(),
            'face_recognition': {
                'confidence_threshold': 0.6,
                'anti_spoofing': True
            },
            'camera': {
                'resolution': [640, 480],
                'fps': 30
            }
        })
        
        # Create sample student (for testing)
        students_ref = db.collection('students').document('sample')
        students_ref.set({
            'student_id': 'STD001',
            'name': 'Sample Student',
            'class': 'Demo Class',
            'active': True,
            'created_at': datetime.now()
        })
        
        # Create attendance collection (empty, will be populated by app)
        attendance_ref = db.collection('attendance').document('_init')
        attendance_ref.set({
            'initialized': True,
            'created_at': datetime.now()
        })
        
        print("✅ Firebase setup completed!")
        print("📊 Collections created:")
        print("   - system (settings)")
        print("   - students (student data)")
        print("   - attendance (attendance records)")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase setup failed: {e}")
        return False

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        db = firestore.client()
        
        # Test read
        doc_ref = db.collection('system').document('settings')
        doc = doc_ref.get()
        
        if doc.exists:
            print("✅ Firebase connection test passed!")
            print(f"📄 System settings: {doc.to_dict()}")
            return True
        else:
            print("❌ Firebase connection test failed - no data found")
            return False
            
    except Exception as e:
        print(f"❌ Firebase connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Student Care System - Firebase Setup")
    print("=" * 50)
    
    # Setup Firebase
    if setup_firebase():
        print("\n🧪 Testing connection...")
        test_firebase_connection()
    
    print("\n📝 Next steps:")
    print("1. Update config.json to use Firebase")
    print("2. Deploy to Google Cloud Run")
    print("3. Add student photos and data")
    print("4. Test face recognition system")