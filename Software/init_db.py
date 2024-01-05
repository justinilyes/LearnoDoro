import sqlite3

from .config import db_path

def initialize_database():

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Courses (
        courseID TEXT PRIMARY KEY
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks (
        taskID TEXT,
        courseID TEXT,
        PRIMARY KEY(taskID, courseID),
        FOREIGN KEY(courseID) REFERENCES Courses(courseID)
    )
    """)

    cursor.execute("""
    ALTER TABLE Courses ADD COLUMN study_time INTEGER DEFAULT 0
    """)

    cursor.execute("""
    ALTER TABLE Tasks ADD COLUMN study_time INTEGER DEFAULT 0
    """)

    cursor.execute("""
    CREATE TABLE StudySessions (
    sessionID INTEGER PRIMARY KEY,
    courseID TEXT NOT NULL,
    taskID TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    study_duration INTEGER NOT NULL,  -- renamed this column
    FOREIGN KEY(courseID) REFERENCES Courses(courseID),
    FOREIGN KEY(taskID, courseID) REFERENCES Tasks(taskID, courseID)
    );
    """)

    conn.commit()
    conn.close()
