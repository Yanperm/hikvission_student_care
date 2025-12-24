#!/bin/bash
# Auto Backup Script - Run daily

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/home/ubuntu/hikvission_student_care"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
cp $PROJECT_DIR/data/database.db $BACKUP_DIR/database_$DATE.db

# Backup code (git commit hash)
cd $PROJECT_DIR
COMMIT_HASH=$(git rev-parse HEAD)
echo $COMMIT_HASH > $BACKUP_DIR/commit_$DATE.txt

# Keep only last 7 days backups
find $BACKUP_DIR -name "database_*.db" -mtime +7 -delete
find $BACKUP_DIR -name "commit_*.txt" -mtime +7 -delete

echo "Backup completed: $DATE"
echo "Commit: $COMMIT_HASH"
