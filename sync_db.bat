@echo off
echo Syncing database from AWS...
scp -i studentcare.pem ubuntu@43.210.87.220:~/hikvission_student_care/data/database.db data/database.db
echo Done! Database synced.
pause
