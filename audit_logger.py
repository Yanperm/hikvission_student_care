"""
Audit Log System
บันทึกการใช้งานระบบทั้งหมด
"""

import sqlite3
from datetime import datetime
import json

class AuditLogger:
    def __init__(self, db_path='data/database.db'):
        self.db_path = db_path
        self.init_table()
    
    def init_table(self):
        """สร้างตาราง audit_logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                username TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                status TEXT DEFAULT 'success'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log(self, action, user_id=None, username=None, resource=None, 
            resource_id=None, details=None, ip_address=None, 
            user_agent=None, status='success'):
        """บันทึก audit log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs 
            (timestamp, user_id, username, action, resource, resource_id, 
             details, ip_address, user_agent, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_id,
            username,
            action,
            resource,
            resource_id,
            json.dumps(details) if details else None,
            ip_address,
            user_agent,
            status
        ))
        
        conn.commit()
        conn.close()
    
    def get_logs(self, limit=100, user_id=None, action=None, resource=None):
        """ดึง audit logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM audit_logs WHERE 1=1'
        params = []
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
        
        if action:
            query += ' AND action = ?'
            params.append(action)
        
        if resource:
            query += ' AND resource = ?'
            params.append(resource)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        logs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return logs
    
    def get_user_activity(self, user_id, days=7):
        """ดึงกิจกรรมของผู้ใช้"""
        from datetime import timedelta
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_logs 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (user_id, start_date))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    def get_stats(self, days=30):
        """สถิติ audit logs"""
        from datetime import timedelta
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total logs
        cursor.execute('SELECT COUNT(*) FROM audit_logs WHERE timestamp >= ?', (start_date,))
        total = cursor.fetchone()[0]
        
        # By action
        cursor.execute('''
            SELECT action, COUNT(*) as count 
            FROM audit_logs 
            WHERE timestamp >= ?
            GROUP BY action 
            ORDER BY count DESC
        ''', (start_date,))
        by_action = dict(cursor.fetchall())
        
        # By user
        cursor.execute('''
            SELECT username, COUNT(*) as count 
            FROM audit_logs 
            WHERE timestamp >= ? AND username IS NOT NULL
            GROUP BY username 
            ORDER BY count DESC 
            LIMIT 10
        ''', (start_date,))
        by_user = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'by_action': by_action,
            'by_user': by_user
        }

# สร้าง instance
audit_logger = AuditLogger()
