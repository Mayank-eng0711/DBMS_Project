import os
from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Set these as environment variables on your deployment platform.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "attendance_db"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def initialize_database():
    # Create the database first (the configured account needs CREATE DATABASE permission).
    config = DB_CONFIG.copy()
    config.pop("database")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_db")
    cursor.close()
    connection.close()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Student (
            student_id INT PRIMARY KEY AUTO_INCREMENT,
            roll_no VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            branch VARCHAR(50) NOT NULL,
            semester INT NOT NULL CHECK (semester BETWEEN 1 AND 12),
            email VARCHAR(100)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id INT PRIMARY KEY AUTO_INCREMENT,
            subject_name VARCHAR(100) NOT NULL,
            subject_code VARCHAR(20) NOT NULL UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT NOT NULL,
            subject_id INT NOT NULL,
            attendance_date DATE NOT NULL,
            status ENUM('Present', 'Absent') NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
            UNIQUE (student_id, subject_id, attendance_date)
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

def error_response(message, status=400):
    return jsonify({"error": message}), status

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/dashboard")
def dashboard():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM Student")
        students = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM Subject")
        subjects = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM Attendance")
        attendance = cursor.fetchone()["total"]
        cursor.close()
        connection.close()
        return jsonify({"students": students, "subjects": subjects, "attendance": attendance})
    except Error:
        app.logger.exception("Dashboard database error")
        return error_response("Could not load dashboard. Check the database connection.", 500)

@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "GET":
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT student_id, roll_no, name, branch, semester, email FROM Student ORDER BY student_id DESC")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify(rows)
        except Error:
            app.logger.exception("Student SELECT error")
            return error_response("Could not load students. Check the database connection.", 500)

    data = request.get_json(silent=True) or {}
    roll_no = str(data.get("roll_no", "")).strip()
    name = str(data.get("name", "")).strip()
    branch = str(data.get("branch", "")).strip()
    email = str(data.get("email", "")).strip() or None
    try:
        semester = int(data.get("semester", 0))
    except (TypeError, ValueError):
        return error_response("Semester must be a number.")
    if not roll_no or not name or not branch:
        return error_response("Roll number, name and branch are required.")
    if not 1 <= semester <= 12:
        return error_response("Semester must be between 1 and 12.")
    if len(roll_no) > 20 or len(name) > 100 or len(branch) > 50 or (email and len(email) > 100):
        return error_response("One or more fields are too long.")

    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """INSERT INTO Student (roll_no, name, branch, semester, email)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (roll_no, name, branch, semester, email))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Student added successfully."}), 201
    except Error as exc:
        app.logger.exception("Student INSERT error")
        if getattr(exc, "errno", None) == 1062:
            return error_response("That roll number already exists.")
        return error_response("Could not save student. Check the database connection and input.")

@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}
    roll_no = str(data.get("roll_no", "")).strip()
    name = str(data.get("name", "")).strip()
    branch = str(data.get("branch", "")).strip()
    email = str(data.get("email", "")).strip() or None
    try:
        semester = int(data.get("semester", 0))
    except (TypeError, ValueError):
        return error_response("Semester must be a number.")
    if not roll_no or not name or not branch or not 1 <= semester <= 12:
        return error_response("Enter valid roll number, name, branch and semester (1–12).")
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """UPDATE Student SET roll_no=%s, name=%s, branch=%s, semester=%s, email=%s
                   WHERE student_id=%s"""
        cursor.execute(query, (roll_no, name, branch, semester, email, student_id))
        connection.commit()
        changed = cursor.rowcount
        cursor.close()
        connection.close()
        if not changed:
            return error_response("Student not found or no changes were made.", 404)
        return jsonify({"message": "Student updated successfully."})
    except Error as exc:
        app.logger.exception("Student UPDATE error")
        if getattr(exc, "errno", None) == 1062:
            return error_response("That roll number already exists.")
        return error_response("Could not update student.")

@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    if request.method == "GET":
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT subject_id, subject_name, subject_code FROM Subject ORDER BY subject_id DESC")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify(rows)
        except Error:
            app.logger.exception("Subject SELECT error")
            return error_response("Could not load subjects. Check the database connection.", 500)

    data = request.get_json(silent=True) or {}
    name = str(data.get("subject_name", "")).strip()
    code = str(data.get("subject_code", "")).strip()
    if not name or not code:
        return error_response("Subject name and code are required.")
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "INSERT INTO Subject (subject_name, subject_code) VALUES (%s, %s)"
        cursor.execute(query, (name, code))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Subject added successfully."}), 201
    except Error as exc:
        app.logger.exception("Subject INSERT error")
        if getattr(exc, "errno", None) == 1062:
            return error_response("That subject code already exists.")
        return error_response("Could not save subject.")

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if request.method == "GET":
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT a.attendance_id, s.roll_no, s.name, sub.subject_name,
                       a.attendance_date, a.status
                FROM Attendance a
                JOIN Student s ON a.student_id = s.student_id
                JOIN Subject sub ON a.subject_id = sub.subject_id
                ORDER BY a.attendance_date DESC, a.attendance_id DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            for row in rows:
                row["attendance_date"] = row["attendance_date"].isoformat()
            return jsonify(rows)
        except Error:
            app.logger.exception("Attendance SELECT error")
            return error_response("Could not load attendance. Check the database connection.", 500)

    data = request.get_json(silent=True) or {}
    try:
        student_id = int(data.get("student_id", 0))
        subject_id = int(data.get("subject_id", 0))
    except (TypeError, ValueError):
        return error_response("Select a valid student and subject.")
    date = str(data.get("attendance_date", "")).strip()
    status = str(data.get("status", "")).strip()
    if not student_id or not subject_id or not date or status not in ("Present", "Absent"):
        return error_response("Select student, subject, date and status.")
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """INSERT INTO Attendance (student_id, subject_id, attendance_date, status)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (student_id, subject_id, date, status))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Attendance marked successfully."}), 201
    except Error as exc:
        app.logger.exception("Attendance INSERT error")
        if getattr(exc, "errno", None) == 1062:
            return error_response("Attendance for this student, subject and date already exists.")
        if getattr(exc, "errno", None) == 1452:
            return error_response("Selected student or subject does not exist.")
        return error_response("Could not mark attendance. Check the date and database.")

@app.route("/attendance/<int:attendance_id>", methods=["PUT"])
def update_attendance(attendance_id):
    data = request.get_json(silent=True) or {}
    date = str(data.get("attendance_date", "")).strip()
    status = str(data.get("status", "")).strip()
    if not date or status not in ("Present", "Absent"):
        return error_response("Enter a valid date and attendance status.")
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "UPDATE Attendance SET attendance_date=%s, status=%s WHERE attendance_id=%s"
        cursor.execute(query, (date, status, attendance_id))
        connection.commit()
        changed = cursor.rowcount
        cursor.close()
        connection.close()
        if not changed:
            return error_response("Attendance record not found or no changes were made.", 404)
        return jsonify({"message": "Attendance updated successfully."})
    except Error:
        app.logger.exception("Attendance UPDATE error")
        return error_response("Could not update attendance. Check for duplicate date records.")

@app.route("/search")
def search_attendance():
    roll_no = request.args.get("roll_no", "").strip()
    if not roll_no:
        return error_response("Enter a roll number.")
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT s.roll_no, s.name, sub.subject_name,
                   COUNT(a.attendance_id) AS total_classes,
                   SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_classes,
                   ROUND(100.0 * SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)
                         / NULLIF(COUNT(a.attendance_id), 0), 2) AS attendance_percentage
            FROM Attendance a
            JOIN Student s ON a.student_id=s.student_id
            JOIN Subject sub ON a.subject_id=sub.subject_id
            WHERE s.roll_no=%s
            GROUP BY s.roll_no, s.name, sub.subject_id, sub.subject_name
            ORDER BY sub.subject_name
        """
        cursor.execute(query, (roll_no,))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(rows)
    except Error:
        app.logger.exception("Attendance search error")
        return error_response("Could not search attendance. Check the database connection.", 500)

if __name__ == "__main__":
    # On first run, create the database and tables using the configured MySQL account.
    try:
        initialize_database()
        print("Database and tables are ready.")
    except Error:
        app.logger.exception("Database initialization failed")
        print("Database initialization failed. Check DB_HOST, DB_USER, DB_PASSWORD and MySQL permissions.")
        raise
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
