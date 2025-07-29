import streamlit as st
from faker import Faker
import mysql.connector
import random
# Step 1: MySQL Connection Setup
conn = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="Sundar_46",  
    database="project_db"
)
cursor = conn.cursor()

fake = Faker()
Faker.seed(0) 
fake_unique = fake.unique
# Step 2: Table Creation
def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        age INT,
        gender VARCHAR(20),
        email VARCHAR(255),
        phone VARCHAR(50),
        enrollment_year INT,
        course_batch VARCHAR(20),
        city VARCHAR(100),
        graduation_year INT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Programming (
        programming_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        language VARCHAR(50),
        problems_solved INT,
        assessments_completed INT,
        mini_projects INT,
        certifications_earned INT,
        latest_project_score INT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SoftSkills (
        soft_skill_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        communication INT,
        teamwork INT,
        presentation INT,
        leadership INT,
        critical_thinking INT,
        interpersonal_skills INT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Placements (
        placement_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        mock_interview_score INT,
        internships_completed INT,
        placement_status VARCHAR(50),
        company_name VARCHAR(255),
        placement_package FLOAT,
        interview_rounds_cleared INT,
        placement_date DATE,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    )
    """)
    conn.commit()
# Step 3: Data Generator Classes
class StudentData:
    def insert_students(self, count=50):
        for _ in range(count):
            name = fake.name()
            age = random.randint(18, 25)
            gender = random.choice(['Male', 'Female', 'Other'])
            email = fake.email()
            phone = fake.phone_number()
            enrollment_year = random.choice([2020, 2021, 2022])
            course_batch = f"{enrollment_year}-{enrollment_year + 4}"
            city = fake.city()
            graduation_year = enrollment_year + 4

            cursor.execute("""
                INSERT INTO Students (name, age, gender, email, phone, enrollment_year, course_batch, city, graduation_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, age, gender, email, phone, enrollment_year, course_batch, city, graduation_year))
        conn.commit()

class RelatedData:
    def insert_related_data(self):
        cursor.execute("SELECT student_id FROM Students")
        student_ids = cursor.fetchall()

        for (student_id,) in student_ids:
            cursor.execute("""
                INSERT INTO Programming (student_id, language, problems_solved, assessments_completed, mini_projects, certifications_earned, latest_project_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id, random.choice(['Python', 'SQL']),
                random.randint(10, 100), random.randint(1, 10), random.randint(0, 5),
                random.randint(0, 3), random.randint(50, 100)
            ))

            cursor.execute("""
                INSERT INTO SoftSkills (student_id, communication, teamwork, presentation, leadership, critical_thinking, interpersonal_skills)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                random.randint(50, 100), random.randint(50, 100), random.randint(50, 100),
                random.randint(50, 100), random.randint(50, 100), random.randint(50, 100)
            ))

            placement_status = random.choice(['Ready', 'Not Ready', 'Placed'])
            company_name = fake.company() if placement_status == 'Placed' else None
            placement_package = round(random.uniform(3, 12), 2) if placement_status == 'Placed' else None
            placement_date = fake.date_this_decade().isoformat() if placement_status == 'Placed' else None

            cursor.execute("""
                INSERT INTO Placements (student_id, mock_interview_score, internships_completed, placement_status, company_name, placement_package, interview_rounds_cleared, placement_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id, random.randint(40, 100), random.randint(0, 3), placement_status,
                company_name, placement_package, random.randint(1, 5), placement_date
            ))

        conn.commit()
# Step 4: Streamlit Interface
import pandas as pd  

def show_streamlit_app():
    st.title("🎓 Placement Eligibility Checker")

    st.sidebar.header("Filter Criteria")
    min_problems = st.sidebar.slider("Minimum Problems Solved", 0, 100, 50)
    min_softskills = st.sidebar.slider("Minimum Avg Soft Skills Score", 0, 100, 75)

    if st.sidebar.button("Generate Fake Data"):
        sd = StudentData()
        rd = RelatedData()
        sd.insert_students()
        rd.insert_related_data()
        st.success("✅ Fake student data inserted into database!")

    query = """
        SELECT s.name, s.age, s.email, p.problems_solved,
               ss.communication, ss.teamwork, ss.presentation, ss.leadership,
               pl.mock_interview_score, pl.placement_status
        FROM Students s
        JOIN Programming p ON s.student_id = p.student_id
        JOIN SoftSkills ss ON s.student_id = ss.student_id
        JOIN Placements pl ON s.student_id = pl.student_id
        WHERE p.problems_solved >= %s
          AND (ss.communication + ss.teamwork + ss.presentation + ss.leadership + ss.critical_thinking + ss.interpersonal_skills)/6 >= %s
    """
    cursor.execute(query, (min_problems, min_softskills))
    data = cursor.fetchall()

    columns = [
        "Name", "Age", "Email", "Problems Solved",
        "Communication", "Teamwork", "Presentation", "Leadership",
        "Mock Interview Score", "Placement Status"
    ]

    if data and len(data[0]) == len(columns):
        df = pd.DataFrame(data, columns=columns)
        st.write("### 🧾 Filtered Eligible Students")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ No eligible students found for the given criteria.")
        if data and len(data[0]) != len(columns):
            st.error("❌ Mismatch between number of columns in query result and defined headers!")

# Run Streamlit App

if __name__ == "__main__":
    create_tables()
    show_streamlit_app()
