"""
Backup and Restore System
สำรองและกู้คืนข้อมูล
"""

import os
import shutil
import sqlite3
from datetime import datetime
import zipfile
import json

class BackupManager:
    def __init__(self, db_path='data/database.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, include_images=True):
        """สร้าง backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup database
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, os.path.join(backup_path, 'database.db'))
        
        # Backup images
        if include_images and os.path.exists('data/students'):
            shutil.copytree('data/students', os.path.join(backup_path, 'students'))
        
        # Backup face model
        if os.path.exists('data/face_model.pkl'):
            shutil.copy2('data/face_model.pkl', os.path.join(backup_path, 'face_model.pkl'))
        
        # Create metadata
        metadata = {
            'timestamp': timestamp,
            'date': datetime.now().isoformat(),
            'include_images': include_images,
            'db_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
        
        with open(os.path.join(backup_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create zip
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove temp folder
        shutil.rmtree(backup_path)
        
        return {
            'success': True,
            'backup_file': zip_path,
            'timestamp': timestamp,
            'size': os.path.getsize(zip_path)
        }
    
    def list_backups(self):
        """แสดงรายการ backup"""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.zip'):
                filepath = os.path.join(self.backup_dir, filename)
                
                # Extract metadata
                try:
                    with zipfile.ZipFile(filepath, 'r') as zipf:
                        if 'metadata.json' in zipf.namelist():
                            metadata = json.loads(zipf.read('metadata.json'))
                        else:
                            metadata = {}
                except:
                    metadata = {}
                
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': os.path.getsize(filepath),
                    'created': datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                    'metadata': metadata
                })
        
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def restore_backup(self, backup_file):
        """กู้คืนข้อมูลจาก backup"""
        if not os.path.exists(backup_file):
            return {'success': False, 'message': 'ไม่พบไฟล์ backup'}
        
        # Create temp restore folder
        restore_path = os.path.join(self.backup_dir, 'restore_temp')
        os.makedirs(restore_path, exist_ok=True)
        
        try:
            # Extract zip
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_path)
            
            # Restore database
            db_backup = os.path.join(restore_path, 'database.db')
            if os.path.exists(db_backup):
                # Backup current database first
                if os.path.exists(self.db_path):
                    shutil.copy2(self.db_path, f"{self.db_path}.before_restore")
                
                shutil.copy2(db_backup, self.db_path)
            
            # Restore images
            students_backup = os.path.join(restore_path, 'students')
            if os.path.exists(students_backup):
                if os.path.exists('data/students'):
                    shutil.rmtree('data/students')
                shutil.copytree(students_backup, 'data/students')
            
            # Restore face model
            model_backup = os.path.join(restore_path, 'face_model.pkl')
            if os.path.exists(model_backup):
                shutil.copy2(model_backup, 'data/face_model.pkl')
            
            # Clean up
            shutil.rmtree(restore_path)
            
            return {'success': True, 'message': 'กู้คืนข้อมูลสำเร็จ'}
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(restore_path):
                shutil.rmtree(restore_path)
            
            return {'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}
    
    def delete_backup(self, backup_file):
        """ลบ backup"""
        if os.path.exists(backup_file):
            os.remove(backup_file)
            return {'success': True, 'message': 'ลบ backup สำเร็จ'}
        return {'success': False, 'message': 'ไม่พบไฟล์ backup'}
    
    def auto_backup(self, keep_days=30):
        """สร้าง backup อัตโนมัติและลบไฟล์เก่า"""
        # Create backup
        result = self.create_backup(include_images=True)
        
        # Delete old backups
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup in self.list_backups():
            created_timestamp = datetime.fromisoformat(backup['created']).timestamp()
            if created_timestamp < cutoff_date:
                self.delete_backup(backup['filepath'])
        
        return result

# สร้าง instance
backup_manager = BackupManager()
