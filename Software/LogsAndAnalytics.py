import sqlite3
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

from .config import db_path

class LogsAndAnalytics:

    def log_study_time(self, courseID, taskID, start_time, end_time, study_duration):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO StudySessions (courseID, taskID, start_time, end_time, study_duration) VALUES (?, ?, ?, ?, ?)",
            (courseID, taskID, start_time, end_time, study_duration)
        )
        conn.commit()
        conn.close()

    def study_time_distribution(self, courses, tasks=None, start_date=None, end_date=None):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        distribution = {}
        # Scenario 3: Only tasks are selected
        if tasks and not courses:
            for task in tasks:
                query = "SELECT SUM(study_duration) FROM StudySessions WHERE taskID = ?"
                params = [task]

                if start_date:
                    query += " AND start_time >= ?"
                    params.append(start_date)
                if end_date:
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                    query += " AND end_time < ?"
                    params.append(end_date_str)

                cursor.execute(query, params)
                result = cursor.fetchone()
                time_studied = result[0] if result[0] else 0
                distribution[task] = time_studied
        else:
            for course in courses:
                # Scenario 1: Only courses are selected
                if not tasks:
                    query = "SELECT SUM(study_duration) FROM StudySessions WHERE courseID = ?"
                    params = [course]

                    if start_date:
                        query += " AND start_time >= ?"
                        params.append(start_date)
                    if end_date:
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                        end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                        query += " AND end_time < ?"
                        params.append(end_date_str)

                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    time_studied = result[0] if result[0] else 0
                    distribution[course] = time_studied
                else:
                    # Scenario 2: Courses and tasks are selected
                    for task in tasks:
                        query = "SELECT SUM(study_duration) FROM StudySessions WHERE courseID = ? AND taskID = ?"
                        params = [course, task]

                        if start_date:
                            query += " AND start_time >= ?"
                            params.append(start_date)
                        if end_date:
                            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                            end_date_str = datetime.strftime(end_date_obj, '%Y-%m-%d')
                            query += " AND end_time < ?"
                            params.append(end_date_str)

                        cursor.execute(query, params)
                        result = cursor.fetchone()
                        time_studied = result[0] if result[0] else 0
                        distribution[task] = time_studied

        conn.close()
        return distribution
    
    def get_daily_study_times(self, selected_courses, selected_tasks, start_date, end_date):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        daily_data = {}

        if selected_courses and not selected_tasks:
            query = """
                SELECT strftime('%Y-%m-%d', start_time) AS formatted_date, courseID, sum(study_duration)
                FROM StudySessions
                WHERE courseID IN ({})
                    AND start_time BETWEEN ? AND ?
                GROUP BY formatted_date, courseID
            """.format(",".join("?" * len(selected_courses)))

            # Modify params to include selected courses, start_date, and end_date
            params = selected_courses + [start_date, end_date]
        elif len(selected_courses) == 1 and selected_tasks:
            # Scenario: One course is selected with tasks
            query = """
                SELECT strftime('%Y-%m-%d', start_time) AS formatted_date, taskID, sum(study_duration)
                FROM StudySessions
                WHERE courseID = ?
                    AND taskID IN ({})
                    AND start_time BETWEEN ? AND ?
                GROUP BY formatted_date, taskID
            """.format(",".join("?" * len(selected_tasks)))

            params = [selected_courses[0]] + selected_tasks + [start_date, end_date]
        else:
            conn.close()
            raise ValueError("Invalid combination of selections")

        cursor.execute(query, params)

        for row in cursor.fetchall():
            date_str, key, study_duration = row
            if key not in daily_data:
                daily_data[key] = []
            daily_data[key].append((date_str, study_duration))

        conn.close()

        return daily_data
    
    def display_pie_chart(self, distribution):
        labels = distribution.keys()
        sizes = distribution.values()
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Study Time Distribution')
        plt.show()

    def display_bar_chart(self, distribution):
        labels = distribution.keys()
        sizes = distribution.values()
        plt.figure(figsize=(8, 6))
        plt.bar(list(labels), list(sizes))
        plt.title('Study Time Distribution (Bar)')
        plt.ylabel('Study Time (mins)')
        plt.xlabel('Courses/Tasks')
        plt.show()

    def display_line_chart(self, daily_distribution):
        if not daily_distribution:
            print("No data available for selected courses/tasks and date range.")
            return

        plt.figure(figsize=(10, 6))

        unique_courses_tasks = set(daily_distribution.keys())
        data_dict = {}
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k'] # TODO: maybe more colors incase more courses/tasks are selected...

        for i, course_task in enumerate(unique_courses_tasks):
            data_dict[course_task] = {
                'dates': [],
                'study_times': [],
                'color': colors[i % len(colors)] 
            }

        for course_task, data in daily_distribution.items():
            for date_str, study_time in data:
                data_dict[course_task]['dates'].append(datetime.strptime(date_str, '%Y-%m-%d'))
                data_dict[course_task]['study_times'].append(study_time)

        for course_task, data in data_dict.items():
            data['dates'], data['study_times'] = zip(*sorted(zip(data['dates'], data['study_times'])))

        for course_task, data in data_dict.items():
            plt.plot(data['dates'], data['study_times'], label=course_task, color=data['color'], marker='o')

        plt.title('Daily Study Time Comparison')
        plt.xlabel('Date')
        plt.ylabel('Study Time (minutes)')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
