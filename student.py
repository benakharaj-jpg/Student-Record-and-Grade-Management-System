import sqlite3
import csv

# ==========================
# Database Setup
# ==========================
def init_db():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            credits INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            grade TEXT,
            FOREIGN KEY(student_id) REFERENCES Students(student_id),
            FOREIGN KEY(course_id) REFERENCES Courses(course_id)
        )
    """)

    conn.commit()
    conn.close()

# ==========================
# Student Functions
# ==========================
def add_student(name, roll_no, email):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Students (name, roll_no, email) VALUES (?, ?, ?)", (name, roll_no, email))
        conn.commit()
        print("✅ Student added successfully.")
    except sqlite3.IntegrityError:
        print("⚠️ Roll number or email already exists.")
    conn.close()

def view_students():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def update_student(student_id, new_name, new_email):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE Students SET name = ?, email = ? WHERE student_id = ?", (new_name, new_email, student_id))
    conn.commit()
    print("✅ Student updated successfully.")
    conn.close()

def delete_student(student_id):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))
    conn.commit()
    print("✅ Student deleted successfully.")
    conn.close()

def search_student(keyword):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE name LIKE ? OR roll_no LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("⚠️ No student found.")
    conn.close()

# ==========================
# Course Functions
# ==========================
def add_course(course_name, credits):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Courses (course_name, credits) VALUES (?, ?)", (course_name, credits))
    conn.commit()
    print("✅ Course added successfully.")
    conn.close()

def view_courses():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Courses")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def update_course(course_id, new_name, new_credits):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE Courses SET course_name = ?, credits = ? WHERE course_id = ?", (new_name, new_credits, course_id))
    conn.commit()
    print("✅ Course updated successfully.")
    conn.close()

def delete_course(course_id):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Courses WHERE course_id = ?", (course_id,))
    conn.commit()
    print("✅ Course deleted successfully.")
    conn.close()

def search_course(keyword):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Courses WHERE course_name LIKE ?", (f"%{keyword}%",))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("⚠️ No course found.")
    conn.close()

# ==========================
# Enrollment & Grades
# ==========================
def enroll_student(student_id, course_id):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
    conn.commit()
    print("✅ Student enrolled in course.")
    conn.close()

def assign_grade(enrollment_id, grade):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE Enrollments SET grade = ? WHERE enrollment_id = ?", (grade, enrollment_id))
    conn.commit()
    print("✅ Grade assigned successfully.")
    conn.close()

def view_enrollments():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT E.enrollment_id, S.name, C.course_name, E.grade
        FROM Enrollments E
        JOIN Students S ON E.student_id = S.student_id
        JOIN Courses C ON E.course_id = C.course_id
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

def view_grades(student_id):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.course_name, E.grade
        FROM Enrollments E
        JOIN Courses C ON E.course_id = C.course_id
        WHERE E.student_id = ?
    """, (student_id,))
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("⚠️ No grades found.")
    conn.close()

def calculate_gpa(student_id, export_csv=False):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT E.grade, C.credits
        FROM Enrollments E
        JOIN Courses C ON E.course_id = C.course_id
        WHERE E.student_id = ?
    """, (student_id,))
    records = cursor.fetchall()
    conn.close()

    if not records:
        print("⚠️ No courses found for this student.")
        return

    grade_points = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
    total_points = 0
    total_credits = 0

    for grade, credits in records:
        if grade in grade_points:
            total_points += grade_points[grade] * credits
            total_credits += credits

    if total_credits == 0:
        print("⚠️ No graded courses yet.")
    else:
        gpa = total_points / total_credits
        print(f"🎓 GPA of student {student_id} = {round(gpa, 2)}")

        if export_csv:
            with open("gpa_report.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Student ID", "GPA"])
                writer.writerow([student_id, round(gpa, 2)])
            print("📂 GPA report exported to gpa_report.csv")

# ==========================
# CLI Menu
# ==========================
def menu():
    init_db()
    while True:
        print("\n===== Student Record & Grade Management =====")
        print("1. Add Student")
        print("2. View Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Search Student")
        print("6. Add Course")
        print("7. View Courses")
        print("8. Update Course")
        print("9. Delete Course")
        print("10. Search Course")
        print("11. Enroll Student")
        print("12. Assign Grade")
        print("13. View Enrollments")
        print("14. View Grades for Student")
        print("15. Calculate GPA")
        print("16. Export GPA Report to CSV")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_student(input("Name: "), input("Roll No: "), input("Email: "))
        elif choice == "2":
            view_students()
        elif choice == "3":
            update_student(int(input("Student ID: ")), input("New Name: "), input("New Email: "))
        elif choice == "4":
            delete_student(int(input("Student ID: ")))
        elif choice == "5":
            search_student(input("Keyword (name/roll no): "))
        elif choice == "6":
            add_course(input("Course Name: "), int(input("Credits: ")))
        elif choice == "7":
            view_courses()
        elif choice == "8":
            update_course(int(input("Course ID: ")), input("New Name: "), int(input("New Credits: ")))
        elif choice == "9":
            delete_course(int(input("Course ID: ")))
        elif choice == "10":
            search_course(input("Keyword (course name): "))
        elif choice == "11":
            enroll_student(int(input("Student ID: ")), int(input("Course ID: ")))
        elif choice == "12":
            assign_grade(int(input("Enrollment ID: ")), input("Grade (A/B/C/D/F): ").upper())
        elif choice == "13":
            view_enrollments()
        elif choice == "14":
            view_grades(int(input("Student ID: ")))
        elif choice == "15":
            calculate_gpa(int(input("Student ID: ")))
        elif choice == "16":
            calculate_gpa(int(input("Student ID: ")), export_csv=True)
        elif choice == "0":
            print("👋 Exiting system.")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

# ==========================
# Run the Program
# ==========================
if __name__ == "__main__":
    menu()
