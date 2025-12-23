# Super Admin API Endpoints
# เพิ่มใน local_app.py

# ============================================
# SUPER ADMIN - SCHOOLS MANAGEMENT
# ============================================

@app.route('/api/super_admin/schools', methods=['GET'])
@super_admin_required
def super_admin_get_schools():
    schools = db.get_all_schools()
    return jsonify({'success': True, 'schools': schools})

@app.route('/api/super_admin/schools/<school_id>', methods=['GET'])
@super_admin_required
def super_admin_get_school(school_id):
    school = db.get_school(school_id)
    if school:
        # Get additional stats
        students = db.get_students(school_id)
        attendance = db.get_attendance(school_id)
        return jsonify({
            'success': True,
            'school': school,
            'stats': {
                'total_students': len(students),
                'total_attendance': len(attendance)
            }
        })
    return jsonify({'success': False, 'message': 'ไม่พบโรงเรียน'})

@app.route('/api/super_admin/schools/<school_id>/renew', methods=['POST'])
@super_admin_required
def super_admin_renew_school(school_id):
    data = request.json
    new_expire_date = data.get('expire_date')
    db.update_school(school_id, {'expire_date': new_expire_date, 'status': 'active'})
    return jsonify({'success': True, 'message': 'ต่ออายุสำเร็จ'})

@app.route('/api/super_admin/schools/<school_id>/suspend', methods=['POST'])
@super_admin_required
def super_admin_suspend_school(school_id):
    db.update_school(school_id, {'status': 'suspended'})
    return jsonify({'success': True, 'message': 'ระงับการใช้งานสำเร็จ'})

@app.route('/api/super_admin/schools/<school_id>/activate', methods=['POST'])
@super_admin_required
def super_admin_activate_school(school_id):
    db.update_school(school_id, {'status': 'active'})
    return jsonify({'success': True, 'message': 'เปิดใช้งานสำเร็จ'})

# ============================================
# SUPER ADMIN - RESELLERS MANAGEMENT
# ============================================

@app.route('/api/resellers', methods=['GET'])
@super_admin_required
def get_resellers():
    resellers = db.get_all_resellers()
    return jsonify({'success': True, 'resellers': resellers})

@app.route('/api/resellers', methods=['POST'])
@super_admin_required
def create_reseller():
    data = request.json
    reseller_id = db.add_reseller(data)
    return jsonify({
        'success': True,
        'reseller_id': reseller_id,
        'username': data['username'],
        'max_schools': data['max_schools'],
        'message': 'สร้าง Reseller สำเร็จ'
    })

@app.route('/api/resellers/<reseller_id>', methods=['GET'])
@super_admin_required
def get_reseller(reseller_id):
    reseller = db.get_reseller(reseller_id)
    if reseller:
        schools = db.get_reseller_schools(reseller_id)
        return jsonify({
            'success': True,
            'reseller': reseller,
            'schools': schools
        })
    return jsonify({'success': False, 'message': 'ไม่พบ Reseller'})

@app.route('/api/resellers/<reseller_id>', methods=['PUT'])
@super_admin_required
def update_reseller(reseller_id):
    data = request.json
    db.update_reseller(reseller_id, data)
    return jsonify({'success': True, 'message': 'อัพเดทข้อมูลสำเร็จ'})

@app.route('/api/resellers/<reseller_id>', methods=['DELETE'])
@super_admin_required
def delete_reseller(reseller_id):
    db.delete_reseller(reseller_id)
    return jsonify({'success': True, 'message': 'ลบ Reseller สำเร็จ'})

@app.route('/api/resellers/<reseller_id>/commission', methods=['GET'])
@super_admin_required
def get_reseller_commission(reseller_id):
    commission = db.calculate_reseller_commission(reseller_id)
    return jsonify({'success': True, 'commission': commission})

# ============================================
# SUPER ADMIN - FINANCE
# ============================================

@app.route('/api/super_admin/payments', methods=['GET'])
@super_admin_required
def get_payments():
    payments = db.get_all_payments()
    return jsonify({'success': True, 'payments': payments})

@app.route('/api/super_admin/payments', methods=['POST'])
@super_admin_required
def add_payment():
    data = request.json
    payment_id = db.add_payment(data)
    return jsonify({'success': True, 'payment_id': payment_id, 'message': 'บันทึกการชำระเงินสำเร็จ'})

@app.route('/api/super_admin/revenue', methods=['GET'])
@super_admin_required
def get_revenue():
    period = request.args.get('period', 'month')
    revenue = db.get_revenue(period)
    return jsonify({'success': True, 'revenue': revenue})

# ============================================
# SUPER ADMIN - REPORTS
# ============================================

@app.route('/api/super_admin/reports/generate', methods=['POST'])
@super_admin_required
def generate_report():
    data = request.json
    report_type = data.get('type')
    period = data.get('period')
    
    if report_type == 'revenue':
        report_data = db.get_revenue_report(period)
    elif report_type == 'schools':
        report_data = db.get_schools_report(period)
    elif report_type == 'resellers':
        report_data = db.get_resellers_report(period)
    elif report_type == 'expiring':
        report_data = db.get_expiring_report()
    else:
        return jsonify({'success': False, 'message': 'ประเภทรายงานไม่ถูกต้อง'})
    
    return jsonify({'success': True, 'report': report_data})

@app.route('/api/super_admin/reports/export', methods=['POST'])
@super_admin_required
def export_report():
    data = request.json
    format_type = data.get('format', 'excel')
    report_data = data.get('data')
    
    if format_type == 'excel':
        # Export to Excel
        file_path = db.export_to_excel(report_data)
    elif format_type == 'pdf':
        # Export to PDF
        file_path = db.export_to_pdf(report_data)
    else:
        return jsonify({'success': False, 'message': 'รูปแบบไม่ถูกต้อง'})
    
    return jsonify({'success': True, 'file_path': file_path, 'message': 'Export สำเร็จ'})

# ============================================
# SUPER ADMIN - NOTIFICATIONS
# ============================================

@app.route('/api/super_admin/notifications/expiring', methods=['POST'])
@super_admin_required
def send_expiring_notifications():
    days = request.json.get('days', 30)
    schools = db.get_expiring_schools(days)
    
    sent = 0
    for school in schools:
        # Send email/SMS
        sent += 1
    
    return jsonify({'success': True, 'sent': sent, 'message': f'ส่งการแจ้งเตือนไปยัง {sent} โรงเรียน'})

# ============================================
# SUPER ADMIN - SETTINGS
# ============================================

@app.route('/api/super_admin/settings', methods=['GET'])
@super_admin_required
def get_settings():
    settings = db.get_system_settings()
    return jsonify({'success': True, 'settings': settings})

@app.route('/api/super_admin/settings', methods=['POST'])
@super_admin_required
def update_settings():
    data = request.json
    db.update_system_settings(data)
    return jsonify({'success': True, 'message': 'บันทึกการตั้งค่าสำเร็จ'})

# ============================================
# SUPER ADMIN - DASHBOARD STATS
# ============================================

@app.route('/api/super_admin/dashboard', methods=['GET'])
@super_admin_required
def get_super_admin_dashboard():
    stats = {
        'total_schools': db.count_schools(),
        'total_resellers': db.count_resellers(),
        'total_students': db.count_all_students(),
        'monthly_revenue': db.get_monthly_revenue(),
        'expiring_soon': db.count_expiring_schools(30),
        'active_rate': db.get_active_rate()
    }
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/super_admin/charts/revenue', methods=['GET'])
@super_admin_required
def get_revenue_chart():
    months = 6
    data = db.get_revenue_chart_data(months)
    return jsonify({'success': True, 'data': data})

@app.route('/api/super_admin/charts/schools', methods=['GET'])
@super_admin_required
def get_schools_chart():
    data = db.get_schools_by_package()
    return jsonify({'success': True, 'data': data})
