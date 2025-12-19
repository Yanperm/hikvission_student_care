from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
DB_PATH = 'cloud_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (student_id TEXT PRIMARY KEY, student_name TEXT, class_name TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, student_name TEXT, 
                  timestamp TEXT, status TEXT)''')
    conn.commit()
    conn.close()

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO attendance (student_id, student_name, timestamp, status) VALUES (?, ?, ?, ?)",
              (data['student_id'], data['student_name'], data['timestamp'], data['status']))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.form if request.files else request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO students (student_id, student_name, class_name, created_at) VALUES (?, ?, ?, ?)",
              (data['student_id'], data['student_name'], data.get('class_name', ''), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

@app.route('/api/attendance/today', methods=['GET'])
def get_today_attendance():
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE DATE(timestamp) = ?", (today,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'student_id': r[1], 'student_name': r[2], 'timestamp': r[3], 'status': r[4]} for r in rows])

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()
    return jsonify([{'student_id': r[0], 'student_name': r[1], 'class_name': r[2]} for r in rows])

@app.route('/')
def dashboard():
    return render_template('cloud_dashboard.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
