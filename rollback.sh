#!/bin/bash
# Rollback Script - Restore to previous version

PROJECT_DIR="/home/ubuntu/hikvission_student_care"
BACKUP_DIR="/home/ubuntu/backups"

echo "Available backups:"
ls -lt $BACKUP_DIR/commit_*.txt | head -5

read -p "Enter backup date (YYYYMMDD_HHMMSS): " BACKUP_DATE

if [ -f "$BACKUP_DIR/commit_$BACKUP_DATE.txt" ]; then
    COMMIT_HASH=$(cat $BACKUP_DIR/commit_$BACKUP_DATE.txt)
    
    echo "Rolling back to commit: $COMMIT_HASH"
    
    cd $PROJECT_DIR
    git reset --hard $COMMIT_HASH
    
    # Restore database
    if [ -f "$BACKUP_DIR/database_$BACKUP_DATE.db" ]; then
        cp $BACKUP_DIR/database_$BACKUP_DATE.db $PROJECT_DIR/data/database.db
        echo "Database restored"
    fi
    
    # Restart app
    pkill -9 python3
    nohup python3 local_app.py > /tmp/app.log 2>&1 &
    
    echo "Rollback completed!"
else
    echo "Backup not found!"
fi
