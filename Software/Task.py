import sqlite3

from .config import db_path

class Task:
    def __init__(self, taskID, courseID):
        self.taskID = taskID
        self.courseID = courseID
    
    def get_taskID(self):
        return self.taskID
    
    def get_courseID(self):
        return self.courseID

    def save_to_db(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try: cursor.execute("INSERT INTO Tasks (taskID, courseID) VALUES (?, ?)", (self.get_taskID(), self.get_courseID()))
        except sqlite3.IntegrityError: print("Task with this name already exists for the selected course.")
        conn.commit()
        conn.close()

    @staticmethod
    def load_tasks_for_course(courseID):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Tasks WHERE courseID=?", (courseID,))
        tasks = cursor.fetchall()
        task_objects = [Task(task[0], task[1]) for task in tasks]
        conn.close()
        return task_objects
    
    @staticmethod
    def delete_from_db(taskID, courseID):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT study_time FROM Tasks WHERE taskID = ? AND courseID = ?", (taskID, courseID))
        result = cursor.fetchone()
        if result:
            task_study_time = result[0]
            cursor.execute("UPDATE Courses SET study_time = study_time - ? WHERE courseID = ?", (task_study_time, courseID))
        cursor.execute("DELETE FROM Tasks WHERE taskID = ? AND courseID = ?", (taskID, courseID))
        cursor.execute("DELETE FROM StudySessions WHERE taskID = ? AND courseID = ?", (taskID, courseID))
        conn.commit()
        conn.close()

