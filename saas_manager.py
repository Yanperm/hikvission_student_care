"""
SaaS Manager - จัดการ Subscription, Plans, Payments
"""
from datetime import datetime, timedelta
import secrets

class SaaSManager:
    def __init__(self, db):
        self.db = db
    
    def get_all_plans(self):
        """ดึงแพ็กเกจทั้งหมด"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plans WHERE is_active = TRUE ORDER BY price')
        plans = cursor.fetchall()
        conn.close()
        return plans
    
    def get_plan(self, plan_id):
        """ดึงข้อมูลแพ็กเกจ"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plans WHERE plan_id = %s', (plan_id,))
        plan = cursor.fetchone()
        conn.close()
        return plan
    
    def create_subscription(self, school_id, plan_id):
        """สร้าง subscription ใหม่"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        subscription_id = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        start_date = datetime.now()
        
        # ถ้าเป็น FREE ให้ trial 30 วัน
        plan = self.get_plan(plan_id)
        if plan_id == 'FREE':
            end_date = start_date + timedelta(days=30)
            status = 'trial'
        else:
            end_date = start_date + timedelta(days=30)  # 1 เดือน
            status = 'active'
        
        cursor.execute('''
            INSERT INTO subscriptions (subscription_id, school_id, plan_id, status, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (subscription_id, school_id, plan_id, status, start_date, end_date))
        
        conn.commit()
        conn.close()
        return subscription_id
    
    def get_school_subscription(self, school_id):
        """ดึง subscription ของโรงเรียน"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, p.name as plan_name, p.max_students, p.max_users, p.features
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.plan_id
            WHERE s.school_id = %s
            ORDER BY s.created_at DESC
            LIMIT 1
        ''', (school_id,))
        subscription = cursor.fetchone()
        conn.close()
        return subscription
    
    def check_subscription_status(self, school_id):
        """ตรวจสอบสถานะ subscription"""
        subscription = self.get_school_subscription(school_id)
        
        if not subscription:
            return {'valid': False, 'reason': 'no_subscription'}
        
        now = datetime.now()
        end_date = subscription['end_date']
        
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        if now > end_date:
            return {'valid': False, 'reason': 'expired', 'expired_date': end_date}
        
        if subscription['status'] == 'cancelled':
            return {'valid': False, 'reason': 'cancelled'}
        
        return {'valid': True, 'subscription': subscription}
    
    def check_usage_limits(self, school_id):
        """ตรวจสอบการใช้งานเทียบกับ limit"""
        subscription = self.get_school_subscription(school_id)
        
        if not subscription:
            return {'exceeded': True, 'reason': 'no_subscription'}
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # นับนักเรียน
        cursor.execute('SELECT COUNT(*) as count FROM students WHERE school_id = %s', (school_id,))
        student_count = cursor.fetchone()['count']
        
        # นับผู้ใช้
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE school_id = %s', (school_id,))
        user_count = cursor.fetchone()['count']
        
        conn.close()
        
        max_students = subscription['max_students']
        max_users = subscription['max_users']
        
        return {
            'exceeded': student_count >= max_students or user_count >= max_users,
            'student_count': student_count,
            'max_students': max_students,
            'user_count': user_count,
            'max_users': max_users
        }
    
    def create_payment(self, school_id, subscription_id, amount, payment_method='bank_transfer'):
        """สร้างรายการชำระเงิน"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO payments (payment_id, school_id, subscription_id, amount, payment_method, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (payment_id, school_id, subscription_id, amount, payment_method, 'pending'))
        
        conn.commit()
        conn.close()
        return payment_id
    
    def confirm_payment(self, payment_id, transaction_id):
        """ยืนยันการชำระเงิน"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE payments 
            SET payment_status = %s, transaction_id = %s, paid_at = %s
            WHERE payment_id = %s
        ''', ('completed', transaction_id, datetime.now(), payment_id))
        
        # ต่ออายุ subscription
        cursor.execute('SELECT school_id, subscription_id FROM payments WHERE payment_id = %s', (payment_id,))
        payment = cursor.fetchone()
        
        if payment:
            cursor.execute('''
                UPDATE subscriptions 
                SET end_date = end_date + INTERVAL '30 days', status = %s
                WHERE subscription_id = %s
            ''', ('active', payment['subscription_id']))
        
        conn.commit()
        conn.close()
    
    def get_school_payments(self, school_id):
        """ดึงประวัติการชำระเงิน"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM payments 
            WHERE school_id = %s 
            ORDER BY created_at DESC
        ''', (school_id,))
        payments = cursor.fetchall()
        conn.close()
        return payments
    
    def record_usage(self, school_id):
        """บันทึกสถิติการใช้งานรายวัน"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('SELECT COUNT(*) as count FROM students WHERE school_id = %s', (school_id,))
        total_students = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE school_id = %s', (school_id,))
        total_users = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM attendance 
            WHERE school_id = %s AND DATE(timestamp) = %s
        ''', (school_id, today))
        total_attendance = cursor.fetchone()['count']
        
        cursor.execute('''
            INSERT INTO usage_stats (school_id, stat_date, total_students, total_users, total_attendance)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (school_id, stat_date) 
            DO UPDATE SET 
                total_students = EXCLUDED.total_students,
                total_users = EXCLUDED.total_users,
                total_attendance = EXCLUDED.total_attendance
        ''', (school_id, today, total_students, total_users, total_attendance))
        
        conn.commit()
        conn.close()
