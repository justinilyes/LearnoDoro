import sqlite3
from datetime import datetime, timedelta
import random

"""
This script generates synthetic data for LearnoDoroApp.db. This way I can test the analytics functionality on large sums of data.
"""

def populate_dummy_data(database_path='project/Software/data/LearnoDoroApp.db'):
    # Establish a connection to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Insert dummy courses
    courses = ['Math', 'Science', 'History', 'English', 'Art']
    for course in courses:
        cursor.execute("INSERT INTO Courses (courseID) VALUES (?)", (course,))

    # Insert dummy tasks
    tasks = ['Homework', 'Project', 'Study for Exam', 'Reading Assignment']
    for course in courses:
        for task in tasks:
            cursor.execute("INSERT INTO Tasks (taskID, courseID) VALUES (?, ?)", (task, course))

    # Generate dummy study sessions
    study_sessions = []
    for _ in range(1000):  # Generate 1000 dummy study sessions
        course = random.choice(courses)
        task = random.choice(tasks)
        start_time = datetime.now() - timedelta(days=random.randint(0, 30))
        end_time = start_time + timedelta(minutes=random.randint(30, 180))
        study_duration = (end_time - start_time).seconds // 60

        study_sessions.append((course, task, start_time, end_time, study_duration))
        cursor.execute("""
            INSERT INTO StudySessions (courseID, taskID, start_time, end_time, study_duration) 
            VALUES (?, ?, ?, ?, ?)
        """, (course, task, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), study_duration))

    # Update the Tasks table with the correct study time
    for course in courses:
        for task in tasks:
            total_time = sum(duration for c, t, _, _, duration in study_sessions if c == course and t == task)
            cursor.execute("""
                UPDATE Tasks SET study_time = ? WHERE courseID = ? AND taskID = ?
            """, (total_time, course, task))

    # Update the Courses table with the correct study time
    for course in courses:
        total_time = sum(duration for c, _, _, _, duration in study_sessions if c == course)
        cursor.execute("""
            UPDATE Courses SET study_time = ? WHERE courseID = ?
        """, (total_time, course))

    # Commit and close
    conn.commit()
    conn.close()
    print("Dummy data has been populated.")

# Call the function to populate the database
populate_dummy_data()
