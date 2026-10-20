import os
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)
_ready = False

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        roll_no VARCHAR(30) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        branch VARCHAR(60) NOT NULL,
        semester INT NOT NULL,
        email VARCHAR(120) NULL)""",
    """CREATE TABLE IF NOT EXISTS subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(30) NOT NULL UNIQUE)""",
    """CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        subject_id INT NOT NULL,
        date DATE NOT NULL,
        status ENUM('Present','Absent') NOT NULL,
        UNIQUE KEY uq (student_id, subject_id, date),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE)""",
]


def conn():
    kw = dict(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "attendance_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    if os.environ.get("DB_SSL") == "1":  # cloud MySQL needs TLS
        kw["ssl"] = {"fake_flag_to_enable_tls": True}
    return pymysql.connect(**kw)


def q(sql, args=(), write=False):
    global _ready
    c = conn()
    try:
        with c.cursor() as cur:
            if not _ready:  # create tables automatically on first call
                for s in SCHEMA:
                    cur.execute(s)
                _ready = True
            cur.execute(sql, args)
            return cur.lastrowid if write else cur.fetchall()
    finally:
        c.close()


@app.errorhandler(pymysql.err.IntegrityError)
def dup(e):
    return jsonify(error="Duplicate or invalid reference: that record already exists or its student/subject is missing."), 409


@app.errorhandler(Exception)
def fail(e):
    code = getattr(e, "code", 500)
    return jsonify(error=str(e)), code if isinstance(code, int) else 500


def need(data, *keys):
    for k in keys:
        if not str(data.get(k, "")).strip():
            raise ValueError(f"{k} is required")


@app.errorhandler(ValueError)
def bad(e):
    return jsonify(error=str(e)), 400


@app.get("/api/stats")
def stats():
    r = q("""SELECT (SELECT COUNT(*) FROM students) students,
                    (SELECT COUNT(*) FROM subjects) subjects,
                    (SELECT COUNT(*) FROM attendance) attendance""")[0]
    return jsonify(r)


@app.get("/api/students")
def students():
    return jsonify(q("SELECT * FROM students ORDER BY roll_no"))


@app.post("/api/students")
def add_student():
    d = request.get_json(force=True)
    need(d, "roll_no", "name", "branch", "semester")
    sem = int(d["semester"])
    q("""INSERT INTO students (roll_no,name,branch,semester,email) VALUES (%s,%s,%s,%s,%s)
         ON DUPLICATE KEY UPDATE name=VALUES(name), branch=VALUES(branch),
         semester=VALUES(semester), email=VALUES(email)""",
      (d["roll_no"].strip(), d["name"].strip(), d["branch"].strip(), sem,
       (d.get("email") or "").strip() or None), write=True)
    return jsonify(ok=True)


@app.delete("/api/students/<int:i>")
def del_student(i):
    q("DELETE FROM students WHERE id=%s", (i,), write=True)
    return jsonify(ok=True)


@app.get("/api/subjects")
def subjects():
    return jsonify(q("SELECT * FROM subjects ORDER BY name"))


@app.post("/api/subjects")
def add_subject():
    d = request.get_json(force=True)
    need(d, "name", "code")
    q("""INSERT INTO subjects (name,code) VALUES (%s,%s)
         ON DUPLICATE KEY UPDATE name=VALUES(name)""",
      (d["name"].strip(), d["code"].strip()), write=True)
    return jsonify(ok=True)


@app.delete("/api/subjects/<int:i>")
def del_subject(i):
    q("DELETE FROM subjects WHERE id=%s", (i,), write=True)
    return jsonify(ok=True)


@app.get("/api/attendance")
def attendance():
    return jsonify(q("""SELECT a.id, s.roll_no, s.name, sub.name AS subject,
        CAST(a.date AS CHAR) AS date, a.status FROM attendance a
        JOIN students s ON s.id=a.student_id JOIN subjects sub ON sub.id=a.subject_id
        ORDER BY a.date DESC, s.roll_no"""))


@app.post("/api/attendance")
def add_attendance():
    d = request.get_json(force=True)
    need(d, "student_id", "subject_id", "date", "status")
    if d["status"] not in ("Present", "Absent"):
        raise ValueError("status must be Present or Absent")
    q("""INSERT INTO attendance (student_id,subject_id,date,status) VALUES (%s,%s,%s,%s)
         ON DUPLICATE KEY UPDATE status=VALUES(status)""",
      (d["student_id"], d["subject_id"], d["date"], d["status"]), write=True)
    return jsonify(ok=True)


@app.delete("/api/attendance/<int:i>")
def del_attendance(i):
    q("DELETE FROM attendance WHERE id=%s", (i,), write=True)
    return jsonify(ok=True)


@app.get("/api/report")
def report():
    roll = request.args.get("roll_no", "").strip()
    rows = q("""SELECT s.roll_no, s.name, sub.name AS subject, COUNT(*) AS total,
        SUM(a.status='Present') AS present FROM attendance a
        JOIN students s ON s.id=a.student_id JOIN subjects sub ON sub.id=a.subject_id
        WHERE (%s='' OR s.roll_no=%s) GROUP BY s.id, sub.id ORDER BY s.roll_no, sub.name""",
             (roll, roll))
    for r in rows:
        r["total"], r["present"] = int(r["total"]), int(r["present"])
        r["percentage"] = round(100 * r["present"] / r["total"], 2)
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
