# app.py (Flask Web Version with SQLite and CSS styling and dynamic port fallback)
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os
import sys
import socket

app = Flask(__name__)

DB_FILE = 'library.db'

# Initialize SQLite DB
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT,
                father_name TEXT,
                address TEXT,
                mobile TEXT,
                shift TEXT,
                joining_date TEXT,
                preparation TEXT,
                seat_no TEXT,
                due_date TEXT,
                discontinue TEXT
            )
        """)
        conn.commit()

init_db()

def get_all_students():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]

def insert_student(student):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            student['id'], student['name'], student['father_name'], student['address'],
            student['mobile'], student['shift'], student['joining_date'], student['preparation'],
            student['seat_no'], student['due_date'], student['discontinue']
        ))
        conn.commit()

def search_student(student_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return dict(zip([column[0] for column in cursor.description], row))
        return None

def mark_discontinued(student_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET discontinue = 'Yes' WHERE id = ?", (student_id,))
        conn.commit()

def get_due_reminders():
    today = datetime.now()
    upcoming = []
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            student = dict(zip([column[0] for column in cursor.description], row))
            try:
                due = datetime.strptime(student['due_date'], "%Y-%m-%d")
                if 0 <= (due - today).days <= 7:
                    upcoming.append(student)
            except:
                continue
    return upcoming

@app.route('/')
def index():
    return render_template('index.html', students=get_all_students())

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student = {
            'id': request.form['id'],
            'name': request.form['name'],
            'father_name': request.form['father_name'],
            'address': request.form['address'],
            'mobile': request.form['mobile'],
            'shift': request.form['shift'],
            'joining_date': request.form['joining_date'],
            'preparation': request.form['preparation'],
            'seat_no': request.form['seat_no'],
            'due_date': request.form['due_date'],
            'discontinue': 'No'
        }
        insert_student(student)
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    result = None
    if request.method == 'POST':
        result = search_student(request.form['id'])
    return render_template('search.html', student=result)

@app.route('/discontinue/<student_id>')
def discontinue(student_id):
    mark_discontinued(student_id)
    return redirect(url_for('index'))

@app.route('/due-reminders')
def due_reminders():
    return render_template('due_reminders.html', students=get_due_reminders())

# Dynamic port fallback if 5000 is unavailable
def find_available_port(start_port=5000, max_tries=10):
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError("No available ports found in range.")

if __name__ == '__main__':
    try:
        port = find_available_port()
        print(f"Starting Flask server on port {port}...")
        app.run(debug=False, host='127.0.0.1', port=port)
    except Exception as e:
        print("Error running Flask app:", e)
        sys.exit(1)
