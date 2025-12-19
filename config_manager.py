import json
import os
from datetime import datetime
import shutil

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_config = {
            "database": {
                "type": "sqlite",
                "config": {
                    "db_path": "data/attendance.db"
                }
            },
            "face_recognition": {
                "confidence_threshold": 0.6,
                "quality_threshold": 0.6,
                "anti_spoofing": True,
                "max_encodings_per_person": 5
            },
            "camera": {
                "resolution": [640, 480],
                "fps": 30,
                "auto_restart": True,
                "detection_interval": 1
            },
            "security": {
                "session_timeout": 24,
                "rate_limit_requests": 100,
                "rate_limit_window": 60,
                "require_auth": True
            },
            "ui": {
                "theme": "light",
                "language": "en",
                "auto_refresh": True,
                "refresh_interval": 1000
            },
            "notifications": {
                "email_enabled": False,
                "sms_enabled": False,
                "webhook_enabled": False
            },
            "backup": {
                "auto_backup": True,
                "backup_interval": 24,
                "max_backups": 7
            }
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults for missing keys
                self.config = self._merge_configs(self.default_config, self.config)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        return self.save_config()
    
    def _merge_configs(self, default, user):
        """Recursively merge user config with defaults"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def backup_config(self):
        """Create backup of current configuration"""
        try:
            backup_dir = 'backups/config'
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'config_backup_{timestamp}.json')
            
            shutil.copy2(self.config_file, backup_file)
            return True, backup_file
        except Exception as e:
            return False, str(e)
    
    def restore_config(self, backup_file):
        """Restore configuration from backup"""
        try:
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.config_file)
                self.load_config()
                return True, "Configuration restored successfully"
            else:
                return False, "Backup file not found"
        except Exception as e:
            return False, str(e)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        return self.save_config()
    
    def validate_config(self):
        """Validate current configuration"""
        errors = []
        
        # Validate database config
        db_type = self.get('database.type')
        if db_type not in ['sqlite', 'mysql', 'firebase']:
            errors.append("Invalid database type")
        
        # Validate face recognition thresholds
        confidence = self.get('face_recognition.confidence_threshold')
        if not (0.1 <= confidence <= 1.0):
            errors.append("Confidence threshold must be between 0.1 and 1.0")
        
        # Validate camera resolution
        resolution = self.get('camera.resolution')
        if not (isinstance(resolution, list) and len(resolution) == 2):
            errors.append("Camera resolution must be [width, height]")
        
        return len(errors) == 0, errors

config_manager = ConfigManager()