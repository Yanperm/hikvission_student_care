#!/bin/bash

# Update local_app.py to use improved database
cat > /tmp/update_local_app.py << 'PYTHON_SCRIPT'
import sys

# Read local_app.py
with open('local_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace database import
old_import = """# Use SQLite by default, RDS only if explicitly enabled
db_type = os.environ.get('DB_TYPE', 'sqlite')

if db_type == 'postgresql' or os.environ.get('USE_POSTGRES', 'false').lower() == 'true':
    try:
        from database_postgres import db
        print("Using PostgreSQL Database")
    except Exception as e:
        print(f"PostgreSQL Connection Failed: {str(e)}")
        print("Falling back to SQLite")
        from database import db
elif os.environ.get('USE_RDS', 'false').lower() == 'true':
    try:
        from database_rds import db
        print("Using RDS Database")
    except Exception as e:
        print(f"RDS Connection Failed: {str(e)}")
        print("Falling back to SQLite")
        from database import db
else:
    from database import db
    print("Using SQLite Database")"""

new_import = """# Use Universal Database (supports both SQLite and PostgreSQL RDS)
try:
    from database_universal import db
except Exception as e:
    print(f"Database initialization failed: {str(e)}")
    print("Falling back to original database")
    from database import db"""

if old_import in content:
    content = content.replace(old_import, new_import)
    with open('local_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Updated local_app.py successfully")
else:
    print("⚠️ Pattern not found, local_app.py may already be updated")
PYTHON_SCRIPT

# Execute on server
ssh -i studentcare.pem ubuntu@43.210.87.220 << 'EOF'
cd /home/ubuntu/studentcare
python3 /tmp/update_local_app.py
EOF
