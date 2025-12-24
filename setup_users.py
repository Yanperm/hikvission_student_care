from database import db
import os

os.makedirs('data', exist_ok=True)

users = [
    ('superadmin', 'admin123', 'Super Admin', 'super_admin', None),
    ('admin', 'admin123', 'Admin', 'admin', 'SCH001'),
    ('teacher1', 'teacher123', 'Teacher 1', 'teacher', 'SCH001'),
    ('parent1', 'parent123', 'Parent 1', 'parent', 'SCH001'),
]

for username, password, name, role, school_id in users:
    try:
        db.add_user(username, password, name, role, school_id)
        print(f'Created: {username}')
    except:
        print(f'Already exists: {username}')

try:
    db.add_school({
        'school_id': 'SCH001',
        'name': 'โรงเรียนสาธิต',
        'address': 'กรุงเทพฯ',
        'phone': '02-xxx-xxxx',
        'status': 'active'
    })
    print('Created school: SCH001')
except:
    print('School already exists')

print('Setup complete!')
