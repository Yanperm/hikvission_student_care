# Database Functions for Super Admin
# เพิ่มใน database.py

def get_all_resellers(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resellers ORDER BY created_at DESC')
    resellers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resellers

def add_reseller(self, data):
    import uuid
    reseller_id = f"RSL{str(uuid.uuid4())[:8].upper()}"
    
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resellers (
            reseller_id, name, package, max_schools, schools_used,
            price, contact_name, phone, email, region,
            expire_date, username, password, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        reseller_id, data['name'], data['package'], data['max_schools'], 0,
        data['price'], data['contact_name'], data['phone'], data['email'],
        data.get('region', ''), data['expire_date'], data['username'],
        data['password'], 'active', datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return reseller_id

def get_reseller(self, reseller_id):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resellers WHERE reseller_id = ?', (reseller_id,))
    reseller = cursor.fetchone()
    conn.close()
    return dict(reseller) if reseller else None

def update_reseller(self, reseller_id, data):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in data.items():
        fields.append(f"{key} = ?")
        values.append(value)
    
    values.append(reseller_id)
    query = f"UPDATE resellers SET {', '.join(fields)} WHERE reseller_id = ?"
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def delete_reseller(self, reseller_id):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM resellers WHERE reseller_id = ?', (reseller_id,))
    conn.commit()
    conn.close()

def get_reseller_schools(self, reseller_id):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schools WHERE reseller_id = ?', (reseller_id,))
    schools = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return schools

def calculate_reseller_commission(self, reseller_id):
    schools = self.get_reseller_schools(reseller_id)
    total = sum(school.get('price', 0) for school in schools)
    
    reseller = self.get_reseller(reseller_id)
    if reseller:
        package = reseller['package']
        if package == 'Basic':
            rate = 0.15
        elif package == 'Pro':
            rate = 0.20
        else:  # Master
            rate = 0.25
        
        commission = total * rate
        return {
            'total_sales': total,
            'commission_rate': rate * 100,
            'commission': commission
        }
    return {'total_sales': 0, 'commission_rate': 0, 'commission': 0}

def get_all_payments(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments ORDER BY payment_date DESC')
    payments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return payments

def add_payment(self, data):
    import uuid
    payment_id = f"PAY{str(uuid.uuid4())[:8].upper()}"
    
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (
            payment_id, school_id, reseller_id, amount, payment_type,
            payment_method, status, notes, payment_date, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        payment_id, data.get('school_id'), data.get('reseller_id'),
        data['amount'], data['payment_type'], data.get('payment_method', 'bank'),
        data.get('status', 'completed'), data.get('notes', ''),
        data.get('payment_date', datetime.now().isoformat()),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return payment_id

def get_revenue(self, period='month'):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    if period == 'today':
        date_filter = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT SUM(amount) FROM payments WHERE date(payment_date) = ? AND status = "completed"', (date_filter,))
    elif period == 'month':
        date_filter = datetime.now().strftime('%Y-%m')
        cursor.execute('SELECT SUM(amount) FROM payments WHERE strftime("%Y-%m", payment_date) = ? AND status = "completed"', (date_filter,))
    elif period == 'year':
        date_filter = datetime.now().strftime('%Y')
        cursor.execute('SELECT SUM(amount) FROM payments WHERE strftime("%Y", payment_date) = ? AND status = "completed"', (date_filter,))
    else:
        cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "completed"')
    
    result = cursor.fetchone()[0]
    conn.close()
    return result or 0

def get_revenue_report(self, period):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    if period == 'month':
        cursor.execute('''
            SELECT strftime("%Y-%m", payment_date) as month, SUM(amount) as total
            FROM payments WHERE status = "completed"
            GROUP BY month ORDER BY month DESC LIMIT 12
        ''')
    elif period == 'year':
        cursor.execute('''
            SELECT strftime("%Y", payment_date) as year, SUM(amount) as total
            FROM payments WHERE status = "completed"
            GROUP BY year ORDER BY year DESC
        ''')
    else:
        cursor.execute('''
            SELECT date(payment_date) as date, SUM(amount) as total
            FROM payments WHERE status = "completed"
            GROUP BY date ORDER BY date DESC LIMIT 30
        ''')
    
    report = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return report

def get_schools_report(self, period):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT package, COUNT(*) as count, SUM(max_students) as total_capacity
        FROM schools GROUP BY package
    ''')
    report = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return report

def get_resellers_report(self, period):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, COUNT(s.school_id) as schools_count
        FROM resellers r
        LEFT JOIN schools s ON r.reseller_id = s.reseller_id
        GROUP BY r.reseller_id
    ''')
    report = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return report

def get_expiring_report(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    days_30 = (today + timedelta(days=30)).isoformat()
    
    cursor.execute('''
        SELECT * FROM schools 
        WHERE expire_date <= ? AND status = "active"
        ORDER BY expire_date ASC
    ''', (days_30,))
    
    schools = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return schools

def get_expiring_schools(self, days):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    target_date = (today + timedelta(days=days)).isoformat()
    
    cursor.execute('''
        SELECT * FROM schools 
        WHERE expire_date <= ? AND expire_date >= ? AND status = "active"
        ORDER BY expire_date ASC
    ''', (target_date, today.isoformat()))
    
    schools = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return schools

def count_schools(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM schools')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_resellers(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM resellers')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_all_students(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_monthly_revenue(self):
    return self.get_revenue('month')

def count_expiring_schools(self, days):
    schools = self.get_expiring_schools(days)
    return len(schools)

def get_active_rate(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM schools WHERE status = "active"')
    active = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM schools')
    total = cursor.fetchone()[0]
    conn.close()
    return round((active / total * 100) if total > 0 else 0, 1)

def get_revenue_chart_data(self, months):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    data = []
    for i in range(months):
        date = datetime.now() - timedelta(days=30*i)
        month = date.strftime('%Y-%m')
        
        cursor.execute('''
            SELECT SUM(amount) FROM payments 
            WHERE strftime("%Y-%m", payment_date) = ? AND status = "completed"
        ''', (month,))
        
        amount = cursor.fetchone()[0] or 0
        data.append({
            'month': date.strftime('%b %Y'),
            'amount': amount
        })
    
    conn.close()
    return list(reversed(data))

def get_schools_by_package(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT package, COUNT(*) as count
        FROM schools GROUP BY package
    ''')
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

def get_system_settings(self):
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings LIMIT 1')
    settings = cursor.fetchone()
    conn.close()
    return dict(settings) if settings else {}

def update_system_settings(self, data):
    conn = self.get_connection()
    cursor = conn.cursor()
    
    # Check if settings exist
    cursor.execute('SELECT COUNT(*) FROM settings')
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        fields = []
        values = []
        for key, value in data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        query = f"UPDATE settings SET {', '.join(fields)}"
        cursor.execute(query, values)
    else:
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO settings ({keys}) VALUES ({placeholders})"
        cursor.execute(query, list(data.values()))
    
    conn.commit()
    conn.close()
