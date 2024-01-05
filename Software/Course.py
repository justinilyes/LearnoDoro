import sqlite3

from .Task import Task
from .config import db_path

class Course:
    def __init__(self, courseID):
        self.courseID = courseID
        self.tasks = Task.load_tasks_for_course(self.courseID)
    
    def get_courseID(self):
        return self.courseID

    def add_task(self, task):
        self.tasks.append(task)

    def save_to_db(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Courses (courseID) VALUES (?)", (self.get_courseID(),))
        conn.commit()
        conn.close()

    def load_tasks_from_db(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks WHERE courseID=?", (self.get_courseID(),))
        tasks_data = cursor.fetchall()
        for task_data in tasks_data:
            task = Task(task_data[0], task_data[1])
            self.tasks.append(task)
        conn.close()

    @classmethod
    def load_all_courses(cls):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT courseID FROM courses")
        courses = cursor.fetchall()
        conn.close()
        return [Course(course_name[0]) for course_name in courses]
    
    @staticmethod
    def delete_from_db(courseID):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Courses WHERE courseID = ?", (courseID,))
        cursor.execute("DELETE FROM StudySessions WHERE courseID = ?", (courseID,))
        cursor.execute("DELETE FROM Tasks WHERE courseID = ?", (courseID,))
        conn.commit()
        conn.close()