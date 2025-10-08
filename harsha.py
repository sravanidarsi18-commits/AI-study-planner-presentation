import sqlite3
import csv
from datetime import datetime, timedelta

# -------------------- Database Setup --------------------
def init_db():
    conn = sqlite3.connect("study_planner.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            difficulty TEXT,
            exam_date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            date TEXT,
            duration INTEGER,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# -------------------- Add Subjects --------------------
def add_subject(name, difficulty, exam_date):
    conn = sqlite3.connect("study_planner.db")
    c = conn.cursor()
    c.execute("INSERT INTO subjects (name, difficulty, exam_date) VALUES (?, ?, ?)", 
              (name, difficulty, exam_date))
    conn.commit()
    conn.close()
    print(f"✅ Subject '{name}' added!")

# -------------------- Generate Weekly Schedule --------------------
def generate_schedule(hours_per_day=4):
    conn = sqlite3.connect("study_planner.db")
    c = conn.cursor()
    c.execute("DELETE FROM schedule")  # clear old schedule

    c.execute("SELECT name, difficulty, exam_date FROM subjects")
    subjects = c.fetchall()

    if not subjects:
        print("⚠️ No subjects found. Please add subjects first.")
        return

    today = datetime.today()
    schedule = []

    # Simple rule: harder subjects get more time
    difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
    total_weight = sum(difficulty_map.get(diff.lower(), 2) for _, diff, _ in subjects)

    for i in range(7):  # schedule for next 7 days
        date = today + timedelta(days=i)
        daily_hours = hours_per_day
        for subject, difficulty, exam_date in subjects:
            weight = difficulty_map.get(difficulty.lower(), 2)
            duration = (weight / total_weight) * hours_per_day
            duration = round(duration, 1)

            if duration > 0:
                c.execute("INSERT INTO schedule (subject, date, duration) VALUES (?, ?, ?)",
                          (subject, date.strftime("%Y-%m-%d"), duration))
                schedule.append((subject, date.strftime("%Y-%m-%d"), duration))

    conn.commit()
    conn.close()
    print("📅 Weekly study plan generated successfully!")
    return schedule

# -------------------- Export to CSV --------------------
def export_schedule():
    conn = sqlite3.connect("study_planner.db")
    c = conn.cursor()
    c.execute("SELECT subject, date, duration, completed FROM schedule")
    rows = c.fetchall()
    conn.close()

    with open("study_schedule.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Date", "Duration(hrs)", "Completed"])
        writer.writerows(rows)
    print("📂 Schedule exported to study_schedule.csv")

# -------------------- Mark Task as Completed --------------------
def mark_completed(schedule_id):
    conn = sqlite3.connect("study_planner.db")
    c = conn.cursor()
    c.execute("UPDATE schedule SET completed=1 WHERE id=?", (schedule_id,))
    conn.commit()
    conn.close()
    print(f"✅ Task {schedule_id} marked as completed!")

# -------------------- Demo --------------------
if __name__ == "__main__":
    init_db()

    # Add sample subjects
    add_subject("Math", "Hard", "2025-11-15")
    add_subject("English", "Easy", "2025-11-20")
    add_subject("Science", "Medium", "2025-11-18")

    # Generate schedule
    plan = generate_schedule(hours_per_day=5)
    for task in plan:
        print(task)

    # Export to CSV
    export_schedule()
