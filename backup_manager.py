import os
import shutil
import zipfile
from datetime import datetime
import json

class BackupManager:
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, include_images=True):
        """Create full system backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'backup_{timestamp}'
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup database
            if os.path.exists('data/attendance.db'):
                shutil.copy2('data/attendance.db', os.path.join(backup_path, 'attendance.db'))
            
            # Backup student data
            if os.path.exists('data/students_data.json'):
                shutil.copy2('data/students_data.json', os.path.join(backup_path, 'students_data.json'))
            
            # Backup face encodings
            if os.path.exists('data/face_images.npy'):
                shutil.copy2('data/face_images.npy', os.path.join(backup_path, 'face_images.npy'))
            if os.path.exists('data/face_labels.npy'):
                shutil.copy2('data/face_labels.npy', os.path.join(backup_path, 'face_labels.npy'))
            
            # Backup configuration
            if os.path.exists('config.json'):
                shutil.copy2('config.json', os.path.join(backup_path, 'config.json'))
            
            # Backup student images
            if include_images and os.path.exists('data/students'):
                shutil.copytree('data/students', os.path.join(backup_path, 'students'))
            
            # Create backup metadata
            metadata = {
                'timestamp': timestamp,
                'date': datetime.now().isoformat(),
                'include_images': include_images,
                'files': os.listdir(backup_path)
            }
            
            with open(os.path.join(backup_path, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create zip archive
            zip_path = f'{backup_path}.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_path)
                        zipf.write(file_path, arcname)
            
            # Remove temporary directory
            shutil.rmtree(backup_path)
            
            return True, zip_path
        except Exception as e:
            return False, str(e)
    
    def restore_backup(self, backup_file):
        """Restore system from backup"""
        try:
            if not os.path.exists(backup_file):
                return False, "Backup file not found"
            
            # Create temporary extraction directory
            temp_dir = os.path.join(self.backup_dir, 'temp_restore')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restore files
            if os.path.exists(os.path.join(temp_dir, 'attendance.db')):
                os.makedirs('data', exist_ok=True)
                shutil.copy2(os.path.join(temp_dir, 'attendance.db'), 'data/attendance.db')
            
            if os.path.exists(os.path.join(temp_dir, 'students_data.json')):
                shutil.copy2(os.path.join(temp_dir, 'students_data.json'), 'data/students_data.json')
            
            if os.path.exists(os.path.join(temp_dir, 'face_images.npy')):
                shutil.copy2(os.path.join(temp_dir, 'face_images.npy'), 'data/face_images.npy')
            
            if os.path.exists(os.path.join(temp_dir, 'face_labels.npy')):
                shutil.copy2(os.path.join(temp_dir, 'face_labels.npy'), 'data/face_labels.npy')
            
            if os.path.exists(os.path.join(temp_dir, 'config.json')):
                shutil.copy2(os.path.join(temp_dir, 'config.json'), 'config.json')
            
            if os.path.exists(os.path.join(temp_dir, 'students')):
                if os.path.exists('data/students'):
                    shutil.rmtree('data/students')
                shutil.copytree(os.path.join(temp_dir, 'students'), 'data/students')
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            return True, "Backup restored successfully"
        except Exception as e:
            return False, str(e)
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip') and file.startswith('backup_'):
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                backups.append({
                    'filename': file,
                    'path': file_path,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'created': file_time.isoformat(),
                    'created_str': file_time.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def delete_backup(self, backup_file):
        """Delete a backup file"""
        try:
            if os.path.exists(backup_file):
                os.remove(backup_file)
                return True, "Backup deleted successfully"
            else:
                return False, "Backup file not found"
        except Exception as e:
            return False, str(e)
    
    def cleanup_old_backups(self, keep_count=7):
        """Keep only the most recent backups"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return True, f"No cleanup needed ({len(backups)} backups)"
        
        deleted_count = 0
        for backup in backups[keep_count:]:
            success, _ = self.delete_backup(backup['path'])
            if success:
                deleted_count += 1
        
        return True, f"Deleted {deleted_count} old backups"

backup_manager = BackupManager()