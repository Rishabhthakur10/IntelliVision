import os
import json
import sqlite3
from datetime import datetime, timedelta
import bcrypt

from src.database.config import supabase, is_supabase_configured

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "intellivision.db")


def hash_pass(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_pass(pwd: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pwd.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        face_embedding TEXT,
        voice_embedding TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        section TEXT NOT NULL,
        teacher_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subject_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        enrolled_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, subject_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        is_present INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    """)

    conn.commit()

    # Seed initial demo data if database is brand new
    cursor.execute("SELECT COUNT(*) FROM teachers")
    teacher_count = cursor.fetchone()[0]

    if teacher_count == 0:
        seed_default_data(conn)

    conn.close()


def seed_default_data(conn):
    cursor = conn.cursor()

    # 1. Default Teachers (password: teacher123 and admin123)
    p1 = hash_pass("teacher123")
    p2 = hash_pass("admin123")
    cursor.execute(
        "INSERT INTO teachers (username, password, name) VALUES (?, ?, ?)",
        ("prof.sharma", p1, "Prof. Vikram Sharma")
    )
    teacher_id_1 = cursor.lastrowid

    cursor.execute(
        "INSERT INTO teachers (username, password, name) VALUES (?, ?, ?)",
        ("admin", p2, "Dr. Elena Vance")
    )
    teacher_id_2 = cursor.lastrowid

    # 2. Default Subjects
    cursor.execute(
        "INSERT INTO subjects (subject_code, name, section, teacher_id) VALUES (?, ?, ?, ?)",
        ("CS101", "Computer Vision & AI", "Section A", teacher_id_1)
    )
    sub1 = cursor.lastrowid

    cursor.execute(
        "INSERT INTO subjects (subject_code, name, section, teacher_id) VALUES (?, ?, ?, ?)",
        ("AI204", "Deep Learning Architectures", "Section B", teacher_id_1)
    )
    sub2 = cursor.lastrowid

    cursor.execute(
        "INSERT INTO subjects (subject_code, name, section, teacher_id) VALUES (?, ?, ?, ?)",
        ("DS301", "Machine Learning in Production", "Section A", teacher_id_2)
    )
    sub3 = cursor.lastrowid

    # 3. Default Students
    students = [
        ("Aarav Mehta", [0.05 * (i % 7) for i in range(128)]),
        ("Ananya Sharma", [0.03 * (i % 5) for i in range(128)]),
        ("Rohan Verma", [0.04 * (i % 6) for i in range(128)]),
        ("Priya Patel", [0.06 * (i % 4) for i in range(128)]),
        ("Kabir Singh", [0.02 * (i % 8) for i in range(128)]),
    ]

    student_ids = []
    for name, emb in students:
        cursor.execute(
            "INSERT INTO students (name, face_embedding) VALUES (?, ?)",
            (name, json.dumps(emb))
        )
        student_ids.append(cursor.lastrowid)

    # 4. Enroll Students
    for sid in student_ids:
        cursor.execute("INSERT OR IGNORE INTO subject_students (student_id, subject_id) VALUES (?, ?)", (sid, sub1))
        if sid in student_ids[:4]:
            cursor.execute("INSERT OR IGNORE INTO subject_students (student_id, subject_id) VALUES (?, ?)", (sid, sub2))
        if sid in student_ids[2:]:
            cursor.execute("INSERT OR IGNORE INTO subject_students (student_id, subject_id) VALUES (?, ?)", (sid, sub3))

    # 5. Seed Attendance Logs for the past 5 sessions
    base_date = datetime.now()
    for day_offset in [10, 7, 5, 2, 1]:
        session_time = (base_date - timedelta(days=day_offset)).strftime("%Y-%m-%dT10:00:00")
        for idx, sid in enumerate(student_ids):
            # simulate 85% attendance
            is_present = 1 if (idx + day_offset) % 4 != 0 else 0
            cursor.execute(
                "INSERT INTO attendance_logs (student_id, subject_id, timestamp, is_present) VALUES (?, ?, ?, ?)",
                (sid, sub1, session_time, is_present)
            )

    conn.commit()


# Ensure DB is created on module load
try:
    init_db()
except Exception:
    pass


# ---------------- TEACHER FUNCTIONS ---------------- #

def check_teacher_exists(username: str) -> bool:
    if is_supabase_configured():
        response = supabase.table("teachers").select("username").eq("username", username).execute()
        return len(response.data) > 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM teachers WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def create_teacher(username: str, password: str, name: str):
    hashed = hash_pass(password)
    if is_supabase_configured():
        data = {"username": username, "password": hashed, "name": name}
        response = supabase.table("teachers").insert(data).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teachers (username, password, name) VALUES (?, ?, ?)",
        (username, hashed, name)
    )
    teacher_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return [{"teacher_id": teacher_id, "username": username, "name": name}]


def teacher_login(username: str, password: str):
    if is_supabase_configured():
        response = supabase.table("teachers").select("*").eq("username", username).execute()
        if response.data:
            teacher = response.data[0]
            if check_pass(password, teacher["password"]):
                return teacher
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teachers WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        teacher = dict(row)
        if check_pass(password, teacher["password"]):
            return teacher
    return None


def get_teacher_subjects(teacher_id: int):
    if is_supabase_configured():
        response = supabase.table("subjects").select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
        subjects = response.data
        for sub in subjects:
            sub["total_students"] = sub.get("subject_students", [{}])[0].get("count", 0) if sub.get("subject_students") else 0
            attendance = sub.get("attendance_logs", [])
            unique_sessions = len(set(log["timestamp"] for log in attendance))
            sub["total_classes"] = unique_sessions
            sub.pop("subject_students", None)
            sub.pop("attendance_logs", None)
        return subjects

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.subject_id, s.subject_code, s.name, s.section, s.teacher_id,
            COUNT(DISTINCT ss.student_id) as total_students,
            COUNT(DISTINCT al.timestamp) as total_classes
        FROM subjects s
        LEFT JOIN subject_students ss ON s.subject_id = ss.subject_id
        LEFT JOIN attendance_logs al ON s.subject_id = al.subject_id
        WHERE s.teacher_id = ?
        GROUP BY s.subject_id
    """, (teacher_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_subject(subject_code: str, name: str, section: str, teacher_id: int):
    if is_supabase_configured():
        data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
        response = supabase.table("subjects").insert(data).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO subjects (subject_code, name, section, teacher_id) VALUES (?, ?, ?, ?)",
        (subject_code, name, section, teacher_id)
    )
    subject_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return [{"subject_id": subject_id, "subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}]


def get_subject_by_code(subject_code: str):
    if is_supabase_configured():
        res = supabase.table("subjects").select("*").eq("subject_code", subject_code).execute()
        return res.data[0] if res.data else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects WHERE subject_code = ?", (subject_code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------- STUDENT FUNCTIONS ---------------- #

def get_all_students():
    if is_supabase_configured():
        response = supabase.table("students").select("*").execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        if item.get("face_embedding") and isinstance(item["face_embedding"], str):
            try:
                item["face_embedding"] = json.loads(item["face_embedding"])
            except Exception:
                pass
        if item.get("voice_embedding") and isinstance(item["voice_embedding"], str):
            try:
                item["voice_embedding"] = json.loads(item["voice_embedding"])
            except Exception:
                pass
        result.append(item)
    return result


def get_student_by_id(student_id: int):
    if is_supabase_configured():
        res = supabase.table("students").select("*").eq("student_id", student_id).execute()
        return res.data[0] if res.data else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        if item.get("face_embedding") and isinstance(item["face_embedding"], str):
            try:
                item["face_embedding"] = json.loads(item["face_embedding"])
            except Exception:
                pass
        return item
    return None


def create_student(new_name: str, face_embedding=None, voice_embedding=None):
    if is_supabase_configured():
        data = {"name": new_name, "face_embedding": face_embedding, "voice_embedding": voice_embedding}
        response = supabase.table("students").insert(data).execute()
        return response.data

    face_json = json.dumps(face_embedding) if face_embedding is not None else None
    voice_json = json.dumps(voice_embedding) if voice_embedding is not None else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, face_embedding, voice_embedding) VALUES (?, ?, ?)",
        (new_name, face_json, voice_json)
    )
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return [{
        "student_id": student_id,
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }]


def enroll_student_to_subject(student_id: int, subject_id: int):
    if is_supabase_configured():
        data = {"student_id": student_id, "subject_id": subject_id}
        response = supabase.table("subject_students").insert(data).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO subject_students (student_id, subject_id) VALUES (?, ?)",
        (student_id, subject_id)
    )
    conn.commit()
    conn.close()
    return [{"student_id": student_id, "subject_id": subject_id}]


def unenroll_student_to_subject(student_id: int, subject_id: int):
    if is_supabase_configured():
        response = supabase.table("subject_students").delete().eq("student_id", student_id).eq("subject_id", subject_id).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM subject_students WHERE student_id = ? AND subject_id = ?",
        (student_id, subject_id)
    )
    conn.commit()
    conn.close()
    return True


def is_student_enrolled(student_id: int, subject_id: int) -> bool:
    if is_supabase_configured():
        res = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject_id).execute()
        return len(res.data) > 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM subject_students WHERE student_id = ? AND subject_id = ?",
        (student_id, subject_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def get_enrolled_students(subject_id: int):
    """
    Returns list of enrolled students formatted as:
    [{"student_id": ..., "subject_id": ..., "students": {"student_id": ..., "name": ...}}]
    """
    if is_supabase_configured():
        res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", subject_id).execute()
        return res.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.student_id, ss.subject_id, s.name, s.face_embedding, s.voice_embedding
        FROM subject_students ss
        JOIN students s ON ss.student_id = s.student_id
        WHERE ss.subject_id = ?
    """, (subject_id,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        face_emb = r["face_embedding"]
        if face_emb and isinstance(face_emb, str):
            try:
                face_emb = json.loads(face_emb)
            except Exception:
                pass
        result.append({
            "student_id": r["student_id"],
            "subject_id": r["subject_id"],
            "students": {
                "student_id": r["student_id"],
                "name": r["name"],
                "face_embedding": face_emb,
                "voice_embedding": r["voice_embedding"]
            }
        })
    return result


def get_student_subjects(student_id: int):
    if is_supabase_configured():
        response = supabase.table("subject_students").select("*, subjects(*)").eq("student_id", student_id).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ss.student_id, ss.subject_id, s.name, s.subject_code, s.section, s.teacher_id
        FROM subject_students ss
        JOIN subjects s ON ss.subject_id = s.subject_id
        WHERE ss.student_id = ?
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "student_id": r["student_id"],
        "subject_id": r["subject_id"],
        "subjects": {
            "subject_id": r["subject_id"],
            "name": r["name"],
            "subject_code": r["subject_code"],
            "section": r["section"],
            "teacher_id": r["teacher_id"]
        }
    } for r in rows]


def get_student_attendance(student_id: int):
    if is_supabase_configured():
        response = supabase.table("attendance_logs").select("*, subjects(*)").eq("student_id", student_id).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT al.log_id, al.student_id, al.subject_id, al.timestamp, al.is_present,
               s.name, s.subject_code, s.section
        FROM attendance_logs al
        JOIN subjects s ON al.subject_id = s.subject_id
        WHERE al.student_id = ?
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "log_id": r["log_id"],
        "student_id": r["student_id"],
        "subject_id": r["subject_id"],
        "timestamp": r["timestamp"],
        "is_present": bool(r["is_present"]),
        "subjects": {
            "name": r["name"],
            "subject_code": r["subject_code"],
            "section": r["section"]
        }
    } for r in rows]


# ---------------- ATTENDANCE FUNCTIONS ---------------- #

def create_attendance(logs: list):
    if not logs:
        return []

    if is_supabase_configured():
        response = supabase.table("attendance_logs").insert(logs).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    for log in logs:
        cursor.execute(
            "INSERT INTO attendance_logs (student_id, subject_id, timestamp, is_present) VALUES (?, ?, ?, ?)",
            (log["student_id"], log["subject_id"], log["timestamp"], 1 if log.get("is_present") else 0)
        )
    conn.commit()
    conn.close()
    return logs


def get_attendance_for_teacher(teacher_id: int):
    if is_supabase_configured():
        response = supabase.table("attendance_logs").select("*, subjects!inner(*)").eq("subjects.teacher_id", teacher_id).execute()
        return response.data

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT al.log_id, al.student_id, al.subject_id, al.timestamp, al.is_present,
               s.name, s.subject_code, s.section
        FROM attendance_logs al
        JOIN subjects s ON al.subject_id = s.subject_id
        WHERE s.teacher_id = ?
        ORDER BY al.timestamp DESC
    """, (teacher_id,))
    rows = cursor.fetchall()
    conn.close()

    return [{
        "log_id": r["log_id"],
        "student_id": r["student_id"],
        "subject_id": r["subject_id"],
        "timestamp": r["timestamp"],
        "is_present": bool(r["is_present"]),
        "subjects": {
            "name": r["name"],
            "subject_code": r["subject_code"],
            "section": r["section"]
        }
    } for r in rows]
