import os
import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import timedelta, datetime
from ttkthemes import ThemedTk
import winsound

from .LogsAndAnalytics import LogsAndAnalytics
from .Settings import Settings
from .Course import Course
from .Task import Task
from .init_db import initialize_database
from .config import db_path, settings_path, sound_path, icon_path

BACKGROUND = '#EAECEE'
BUTTON_BACKGROUND = '#5DADE2'
BUTTON_FOREGROUND = '#D2B4DE'
HOVER_BACKGROUND = '#3498DB'
LABEL_FOREGROUND = '#17202A'
ANALYTICS_COURSETASK_BACKGROUND = '#D7DBDD'

class LearnoDoroApp(ThemedTk):
    def __init__(self):
        super().__init__()

        self.title('LearnoDoro')
        self.configure(bg=BACKGROUND)

        style = ttk.Style()
        style.theme_use('breeze')
        style.configure("TFrame", background=BACKGROUND)
        style.configure("TButton",
                        font=("Arial", 14),
                        padding=(10, 5),
                        background=BUTTON_BACKGROUND,
                        foreground=BUTTON_FOREGROUND)
        style.map("TButton",
                background=[('active', HOVER_BACKGROUND)],
                foreground=[('active', '#7FB3D5')])
        style.configure("TLabel",
                        background=BACKGROUND,
                        foreground=LABEL_FOREGROUND)
        style.configure("Heading.TLabel",
                        background=BACKGROUND,
                        foreground=LABEL_FOREGROUND)
        
        self.iconbitmap(icon_path)
        
        if not os.path.isfile(db_path):
            initialize_database()

        self.settings = Settings()
        if not settings_path.is_file():
            self.settings.save_to_file(settings_path)
        self.settings.load_from_file(settings_path)

        self.courses = {}
        for course in Course.load_all_courses():
            self.courses[course.get_courseID()] = course

        self.current_course = None
        self.current_task = None

        self.study_duration_seconds = 0

        self.logs_and_analytics = LogsAndAnalytics()
        self.show_graph_var = tk.IntVar()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 600
        window_height = 550
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)

        main_frame = ttk.Frame(self)
        main_frame.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        # main_frame.grid_columnconfigure(1, weight=1)
        # main_frame.grid_columnconfigure(2, weight=1)
        # main_frame.grid_columnconfigure(3, weight=1)

        self.course_label = ttk.Label(main_frame, text="Course: None Selected", style="Heading.TLabel", font=("Arial", 25))
        self.course_label.grid(row=1, column=1, columnspan=3, pady=(20, 10), sticky=tk.W)

        self.task_label = ttk.Label(main_frame, text="Task: None Selected", style="Heading.TLabel", font=("Arial", 25))
        self.task_label.grid(row=2, column=1, columnspan=3, pady=(10, 20), sticky=tk.W)
        
        self.add_course_button = ttk.Button(main_frame, text="Add Course", command=self.add_course, style="TButton")
        self.add_course_button.grid(row=3, column=1, pady=10, padx=10)
        
        self.course_combobox = ttk.Combobox(main_frame, values=list(self.courses.keys()), postcommand=self.update_course_combobox, state="readonly")
        self.course_combobox.grid(row=3, column=2, pady=10, padx=10)
        self.course_combobox.bind("<<ComboboxSelected>>", self.on_course_selected)

        self.delete_course_button = ttk.Button(main_frame, text="Delete Course", command=self.delete_course, style="TButton")
        self.delete_course_button.grid(row=3, column=3, pady=10, padx=10)
        
        self.add_task_button = ttk.Button(main_frame, text="Add Task", command=self.add_task, style="TButton")
        self.add_task_button.grid(row=4, column=1, pady=10, padx=10)

        self.task_combobox = ttk.Combobox(main_frame, postcommand=self.update_task_combobox, state="readonly")
        self.task_combobox.grid(row=4, column=2, pady=10, padx=10)
        self.task_combobox.bind("<<ComboboxSelected>>", self.on_task_selected)

        self.delete_task_button = ttk.Button(main_frame, text="Delete Task", command=self.delete_task, style="TButton")
        self.delete_task_button.grid(row=4, column=3, pady=10, padx=10)
        
        self.timer_var = tk.StringVar(value=f"{self.settings.study_time.seconds // 60:02}:00")

        timer_display = ttk.Label(main_frame, textvariable=self.timer_var, font=("Arial", 48))
        timer_display.grid(row=5, column=2, columnspan=1, pady=20)

        self.start_button = ttk.Button(main_frame, text="Start", command=self.start_timer, style="TButton")
        self.start_button.grid(row=5, column=1, pady=10, padx=10)

        self.stop_button = ttk.Button(main_frame, text="Stop", command=self.stop_timer, style="TButton", state=tk.DISABLED)
        self.stop_button.grid(row=5, column=3, pady=10, padx=10)

        self.state_label = ttk.Label(main_frame, text="Idle", style="Heading.TLabel", font=("Arial", 25))
        self.state_label.grid(row=6, column=2, pady=20, sticky=tk.NS)

        self.settings_button = ttk.Button(main_frame, text="Settings", command=self.open_settings, style="TButton")
        self.settings_button.grid(row=7, column=1, columnspan=2, pady=10)

        self.analytics_button = ttk.Button(main_frame, text="Analytics", command=self.open_analytics_window)
        self.analytics_button.grid(row=7, column=2, columnspan=2, pady=10)
        
        main_frame.grid_rowconfigure(9, weight=1)
        
        main_frame.grid_columnconfigure(4, weight=1)

        for i in range(10):
            main_frame.grid_rowconfigure(i, weight=1)

        for i in range(4):
            main_frame.grid_columnconfigure(i, weight=1)

        self.state = "study"
        self.running = False
        self.time_left = self.settings.study_time
        self.pomodoros_completed = 0

    def set_course_task_widgets_state(self, state):
        """Set the state of course and task-related widgets."""
        self.course_combobox["state"] = state
        self.add_course_button["state"] = state
        self.task_combobox["state"] = state
        self.add_task_button["state"] = state
        self.settings_button["state"] = state
        self.analytics_button["state"] = state
        self.delete_course_button["state"] = state
        self.delete_task_button["state"] = state
        self.start_button["state"] = state

    def refresh_app_state(self):
        mins = self.settings.study_time.seconds // 60
        self.timer_var.set(f"{mins:02}:00")

    def start_timer(self):
        if not self.current_course:
            messagebox.showerror("No Course Selected", "Please select a course before starting the timer.")
            return
        self.state = "study"
        self.pomodoros_completed = 0
        self.running = True
        self.stop_button["state"] = tk.NORMAL
        self.update_timer()
        self.start_timestamp = datetime.now()
        self.start_timestamp = self.start_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.set_course_task_widgets_state(tk.DISABLED)

    def stop_timer(self):
        self.running = False
        self.stop_button["state"] = tk.DISABLED
        self.time_left = self.settings.study_time
        mins = self.time_left.seconds // 60
        self.timer_var.set(f"{mins:02}:00")
        self.end_timestamp = datetime.now()
        self.end_timestamp = self.end_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.log_study_session()
        self.update_study_time()
        self.study_duration_seconds = 0
        self.pomodoros_completed = 0
        self.set_course_task_widgets_state(tk.NORMAL)

    def reset_timer(self):
        self.time_left = self.settings.study_time
        mins = self.time_left.seconds // 60
        self.timer_var.set(f"{mins:02}:00")

    def update_timer(self):
        if self.running:
            mins, secs = divmod(self.time_left.seconds, 60)
            self.timer_var.set(f"{mins:02}:{secs:02}")

            state_text = self.state.replace("_", " ").title()
            self.state_label.config(text=state_text)
            if self.time_left == timedelta(0):
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME)
                if self.state == "study":
                    self.pomodoros_completed += 1
                    if self.pomodoros_completed % self.settings.long_break_intervals == 0:
                        self.state = "long_break"
                        self.time_left = self.settings.long_break_length
                    else:
                        self.state = "short_break"
                        self.time_left = self.settings.short_break_length
                elif self.state in ["short_break", "long_break"]:
                    self.state = "study"
                    self.time_left = self.settings.study_time
                self.update_timer() 
            else:
                if self.state == "study":
                    self.study_duration_seconds += 1
                self.time_left -= timedelta(seconds=1)
                self.after(1000, self.update_timer)

    def update_study_time(self):
        if self.study_duration_seconds < 60: return
        study_duration = self.study_duration_seconds // 60
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE Courses SET study_time = study_time + ? WHERE courseID = ?", (study_duration, self.current_course.get_courseID()))
        if self.current_task: cursor.execute("UPDATE Tasks SET study_time = study_time + ? WHERE taskID = ? AND courseID = ?", (study_duration, self.current_task.get_taskID(), self.current_course.get_courseID()))
        conn.commit()
        conn.close()

    def add_course(self):
        courseID = simpledialog.askstring("Add Course", "Enter the name of the new course:")
        if not courseID:
            return

        courseID = courseID.strip()

        if not courseID:
            messagebox.showerror("Invalid Input", "Course name cannot be empty or just whitespace.")
            return

        if not all(char.isalnum() or char.isspace() for char in courseID):
            messagebox.showerror("Invalid Input", "Course name can only contain letters, numbers, and spaces.")
            return

        if courseID in self.courses:
            messagebox.showerror("Duplicate Course", "A course with this name already exists.")
            return

        course = Course(courseID)
        course.save_to_db()
        self.courses[courseID] = course
        self.current_course = course
        self.course_label.config(text=f"Course: {courseID}")

        self.current_task = None
        self.task_label.config(text="Task: None Selected")

        self.update_course_combobox()
        self.course_combobox.set(courseID)

    def delete_course(self):
        courseID = self.course_combobox.get()
        if courseID:
            confirm = messagebox.askyesno("Delete Course", f"Are you sure you want to delete the course '{courseID}'?")
            if confirm:
                if courseID in self.courses:
                    Course.delete_from_db(courseID)
                    del self.courses[courseID]
                self.update_course_combobox()
                self.current_course = None
                self.course_label.config(text="Course: None Selected")
                self.task_label.config(text="Task: None Selected")
                self.task_combobox.set('')
                self.task_combobox["values"] = []
        else:
            messagebox.showerror("No Course Selected", "Please select a course to delete.")

    def update_course_combobox(self):
        self.course_combobox["values"] = list(self.courses.keys())

    def on_course_selected(self, event):
        courseID = self.course_combobox.get()
        if courseID in self.courses:
            self.current_course = self.courses[courseID]
            self.current_course.load_tasks_from_db()
            self.course_label.config(text=f"Course: {courseID}")
            self.current_task = None
            self.task_combobox.set('')
            self.task_label.config(text="Task: None Selected")
            self.update_task_combobox()

    def add_task(self):
        if not self.current_course:
            messagebox.showerror("No Course Selected", "Please select a course before adding a task.")
            return

        taskID = simpledialog.askstring("Add Task", "Enter the name of the new task:")
        if not taskID:
            return

        taskID = taskID.strip()

        if not taskID:
            messagebox.showerror("Invalid Input", "Task name cannot be empty or just whitespace.")
            return

        if not all(char.isalnum() or char.isspace() for char in taskID):
            messagebox.showerror("Invalid Input", "Task name can only contain letters, numbers, and spaces.")
            return

        if any(task.get_taskID() == taskID for task in self.current_course.tasks):
            messagebox.showerror("Duplicate Task", "A task with this name already exists in the selected course.")
            return

        task = Task(taskID, self.current_course.get_courseID())
        task.save_to_db()
        self.current_course.add_task(task)
        self.current_task = task
        self.task_label.config(text=f"Task: {taskID}")

        self.update_task_combobox()
        self.task_combobox.set(taskID)

    def delete_task(self):
        taskID = self.task_combobox.get()
        if taskID and self.current_course:
            confirm = messagebox.askyesno("Delete Task", f"Are you sure you want to delete the task '{taskID}'?")
            if confirm:
                Task.delete_from_db(taskID, self.current_course.get_courseID())
                self.update_task_combobox()
                self.current_task = None
                self.task_label.config(text="Task: None Selected")
        else:
            messagebox.showerror("No Task Selected", "Please select a task to delete.")

    def update_task_combobox(self):
        if self.current_course:
            courseID = self.current_course.get_courseID()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT taskID FROM tasks WHERE courseID=?", (courseID,))
            tasks = cursor.fetchall()
            taskIDs = [task[0] for task in tasks]
            taskIDs.insert(0, '')
            self.task_combobox["values"] = taskIDs
            conn.close()
        else:
            self.task_combobox["values"] = ['']

    def on_task_selected(self, event):
        taskID = self.task_combobox.get()
        for task in self.current_course.tasks:
            if task.get_taskID() == taskID:
                self.current_task = task
                self.task_label.config(text=f"Task: {taskID}")
                return
        self.current_task = None
        self.task_label.config(text="Task: None Selected")

    def open_settings(self):
        self.settings_window = tk.Toplevel(self)
        self.settings_window.title("Settings")
        window_width = 305
        window_height = 280
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        x = main_x + (main_width - window_width) // 2
        y = main_y + (main_height - window_height) // 2
        self.settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.settings_window.resizable(False, False)
        self.settings_window.grab_set()
        self.settings_window.transient(self)
        self.settings_window.configure(bg=BACKGROUND)
        self.settings_window.iconbitmap(icon_path)

        study_time_label = ttk.Label(self.settings_window, text="Study Time (minutes):")
        study_time_label.grid(row=1, column=0)
    
        self.study_time_entry = ttk.Entry(self.settings_window)
        self.study_time_entry.insert(0, str(self.settings.study_time.seconds // 60))
        self.study_time_entry.grid(row=1, column=1)

        short_break_label = ttk.Label(self.settings_window, text="Short Break (minutes):")
        short_break_label.grid(row=2, column=0)

        self.short_break_entry = ttk.Entry(self.settings_window)
        self.short_break_entry.insert(0, str(self.settings.short_break_length.seconds // 60))
        self.short_break_entry.grid(row=2, column=1)

        long_break_label = ttk.Label(self.settings_window, text="Long Break (minutes):")
        long_break_label.grid(row=3, column=0)

        self.long_break_entry = ttk.Entry(self.settings_window)
        self.long_break_entry.insert(0, str(self.settings.long_break_length.seconds // 60))
        self.long_break_entry.grid(row=3, column=1)

        long_break_intervals_label = ttk.Label(self.settings_window, text="Long Break Intervals: ")
        long_break_intervals_label.grid(row=4, column=0)

        self.long_break_intervals_entry = ttk.Entry(self.settings_window)
        self.long_break_intervals_entry.insert(0, str(self.settings.long_break_intervals))
        self.long_break_intervals_entry.grid(row=4, column=1)

        save_button = ttk.Button(self.settings_window, text="Save Changes", command=self.save_changes)
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

        close_button = ttk.Button(self.settings_window, text="Close", command=self.settings_window.destroy)
        close_button.grid(row=6, column=0, columnspan=2, pady=10)
  
        study_time_label.grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.study_time_entry.grid(row=0, column=1, pady=5, padx=5)

        short_break_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.short_break_entry.grid(row=1, column=1, pady=5, padx=5)

        long_break_label.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.long_break_entry.grid(row=2, column=1, pady=5, padx=5)

        long_break_intervals_label.grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.long_break_intervals_entry.grid(row=3, column=1, pady=5, padx=5)

        self.settings_window.wait_window()

    def save_changes(self):
        try:
            study_time_val = int(self.study_time_entry.get())
            short_break_val = int(self.short_break_entry.get())
            long_break_val = int(self.long_break_entry.get())
            long_break_intervals_val = int(self.long_break_intervals_entry.get())

            if not (1 <= study_time_val <= 90):
                raise ValueError("Study time must be between 1 and 90 minutes.")
            if not (1 <= short_break_val <= 90):
                raise ValueError("Short break must be between 1 and 90 minutes.")
            if not (1 <= long_break_val <= 90):
                raise ValueError("Long break must be between 1 and 90 minutes.")
            if not (0 <= long_break_intervals_val):
                raise ValueError("The intervals of long breaks occuring cannot be negative.")

            self.settings.study_time = timedelta(minutes=study_time_val)
            self.settings.short_break_length = timedelta(minutes=short_break_val)
            self.settings.long_break_length = timedelta(minutes=long_break_val)
            self.settings.long_break_intervals = long_break_intervals_val

            self.settings.save_to_file(settings_path)
            self.refresh_app_state()
            self.reset_timer()
            messagebox.showinfo("Settings", "Changes saved successfully!")

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def log_study_session(self):
        if self.study_duration_seconds < 60: return
        study_duration = self.study_duration_seconds // 60
        taskID = self.current_task.get_taskID() if self.current_task else None
        self.logs_and_analytics.log_study_time(self.current_course.get_courseID(), taskID, self.start_timestamp, self.end_timestamp, study_duration)

    def open_analytics_window(self):
        self.analytics_window = tk.Toplevel(self)
        self.analytics_window.title("Analytics")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 815
        window_height = 530
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.analytics_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.analytics_window.resizable(False, False)
        self.analytics_window.grab_set()
        self.analytics_window.transient(self)
        self.analytics_window.configure(bg=BACKGROUND)
        self.analytics_window.iconbitmap(icon_path)
        
        course_scroll = tk.Scrollbar(self.analytics_window, orient=tk.VERTICAL)
        course_scroll.grid(row=0, column=2, sticky=tk.W + tk.NS)

        task_scroll = tk.Scrollbar(self.analytics_window, orient=tk.VERTICAL)
        task_scroll.grid(row=1, column=2, sticky=tk.W + tk.NS)

        self.analytics_course_listbox = tk.Listbox(
            self.analytics_window,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            yscrollcommand=course_scroll.set,
            bg=BACKGROUND,
            fg=LABEL_FOREGROUND,
            selectbackground=ANALYTICS_COURSETASK_BACKGROUND
        )
        self.analytics_course_listbox.grid(row=0, column=0, columnspan=2, sticky=tk.EW)

        self.analytics_task_listbox = tk.Listbox(
            self.analytics_window,
            selectmode=tk.MULTIPLE,
            exportselection=False,
            yscrollcommand=task_scroll.set,
            bg=BACKGROUND,
            fg=LABEL_FOREGROUND,
            selectbackground=ANALYTICS_COURSETASK_BACKGROUND
        )
        self.analytics_task_listbox.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

        course_scroll.config(command=self.analytics_course_listbox.yview)
        task_scroll.config(command=self.analytics_task_listbox.yview)

        for course in self.courses:
            self.analytics_course_listbox.insert(tk.END, course)

        self.analytics_course_listbox.bind("<<ListboxSelect>>", self.update_analytics_task_listbox)

        self.placeholder_text = 'YYYY-MM-DD'

        ttk.Label(self.analytics_window, text="Start Date:").grid(row=0, column=3, pady=10, padx=10, sticky=tk.NW)
        self.start_date_entry = ttk.Entry(self.analytics_window, foreground="grey")
        self.start_date_entry.grid(row=0, column=4, pady=10, padx=10, sticky=tk.NW)
        self.start_date_entry.insert(0, self.placeholder_text)
        self.start_date_entry.bind("<FocusIn>", self.on_start_entry_click)
        self.start_date_entry.bind("<FocusOut>", self.on_start_focusout)

        ttk.Label(self.analytics_window, text="End Date:").grid(row=0, column=3, pady=10, padx=10, sticky=tk.W)
        self.end_date_entry = ttk.Entry(self.analytics_window, foreground="grey")
        self.end_date_entry.grid(row=0, column=4, pady=10, padx=10, sticky=tk.W)
        self.end_date_entry.insert(0, self.placeholder_text)
        self.end_date_entry.bind("<FocusIn>", self.on_end_entry_click)
        self.end_date_entry.bind("<FocusOut>", self.on_end_focusout)

        ttk.Style(self.analytics_window).configure('Analytics.TCheckbutton', background=BACKGROUND, foreground=LABEL_FOREGROUND)

        show_graph_checkbutton = ttk.Checkbutton(
                                    self.analytics_window, 
                                    text="Show Graph", 
                                    variable=self.show_graph_var, 
                                    style='Analytics.TCheckbutton')
        show_graph_checkbutton.grid(row=0, column=3, columnspan=2, pady=10, sticky=tk.S)

        ttk.Label(self.analytics_window, text="Chart Type:").grid(row=1, column=3, pady=10, padx=10, sticky=tk.N)
        self.chart_type_combobox = ttk.Combobox(self.analytics_window, values=["Pie Chart", "Line Chart", "Bar Chart"], state='readonly')
        self.chart_type_combobox.set("Pie Chart")
        self.chart_type_combobox.grid(row=1, column=4, pady=10, padx=10, sticky=tk.N)

        self.display_analytics_button = ttk.Button(self.analytics_window, text="Display Analytics", command=self.display_analytics)
        self.display_analytics_button.grid(row=1, column=3, columnspan=2, pady=10)

        self.export_csv_button = ttk.Button(self.analytics_window, text="Export Study Logs to CSV", command=self.export_to_csv)
        self.export_csv_button.grid(row=1, column=3, columnspan=2, pady=10, sticky=tk.S)

        results_scroll = tk.Scrollbar(self.analytics_window, orient=tk.VERTICAL)

        self.results_text = tk.Text(self.analytics_window, wrap=tk.WORD, width=75, height=10, state='disabled', yscrollcommand=results_scroll.set)
        self.results_text.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.EW)

        results_scroll.config(command=self.results_text.yview)
        results_scroll.grid(row=4, column=2, sticky=tk.NS + tk.E)

        self.analytics_window.wait_window()

    def on_start_entry_click(self, event):
        """Event handler for when the Entry widget gets focus."""
        if self.start_date_entry.get() == self.placeholder_text:
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.config(foreground='black')

    def on_start_focusout(self, event):
        """Event handler for when the Entry widget loses focus."""
        if not self.start_date_entry.get():
            self.start_date_entry.insert(0, self.placeholder_text)
            self.start_date_entry.config(foreground='grey')

    def on_end_entry_click(self, event):
        """Event handler for when the end date Entry widget gets focus."""
        if self.end_date_entry.get() == self.placeholder_text:
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.config(foreground='black')

    def on_end_focusout(self, event):
        """Event handler for when the end date Entry widget loses focus."""
        if not self.end_date_entry.get():
            self.end_date_entry.insert(0, self.placeholder_text)
            self.end_date_entry.config(foreground='grey')

    def update_analytics_task_listbox(self, event):
        self.analytics_task_listbox.delete(0, tk.END)

        selected_courses = [self.analytics_course_listbox.get(i) for i in self.analytics_course_listbox.curselection()]

        if len(selected_courses) == 1:
            course = selected_courses[0]
            if course in self.courses:
                course = Course(course)
                for task in course.tasks:
                    self.analytics_task_listbox.insert(tk.END, task.get_taskID())

        for i, course in enumerate(self.courses):
            if course in selected_courses:
                self.analytics_course_listbox.selection_set(i)

    def validate_courses_and_dates(self):
        self.display_analytics_button.config(state='disabled')
        self.export_csv_button.config(state='disabled')
        
        selected_courses = [self.analytics_course_listbox.get(i) for i in self.analytics_course_listbox.curselection()]
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        error_occurred = False

        if not selected_courses:
            messagebox.showerror("No Courses Selected", "At least one course has to be selected.", parent=self)
            error_occurred = True

        elif not start_date_str or not end_date_str:
            messagebox.showerror("Missing Date", "Both start date and end date must be provided.", parent=self)
            error_occurred = True

        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
                end_date = (datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)).date() if end_date_str else None
            except ValueError:
                messagebox.showerror("Invalid Date Format", "Please enter the date in YYYY-MM-DD format.", parent=self)
                error_occurred = True

            if not error_occurred and start_date and end_date and start_date >= end_date:
                messagebox.showerror("Invalid Date", "Start date must be before end date.", parent=self)
                error_occurred = True

        self.display_analytics_button.config(state='normal')
        self.export_csv_button.config(state='normal')

        if error_occurred:
            return None, None, None

        return selected_courses, start_date, end_date

    def display_analytics(self):
        selected_courses, start_date, end_date = self.validate_courses_and_dates()
        if selected_courses is None or start_date is None or end_date is None:
            return
            
        selected_tasks = [self.analytics_task_listbox.get(i) for i in self.analytics_task_listbox.curselection()]
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        if selected_tasks:
            distribution = self.logs_and_analytics.study_time_distribution(selected_courses, selected_tasks, start_date_str, end_date_str)
        else:
            distribution = self.logs_and_analytics.study_time_distribution(selected_courses, None, start_date_str, end_date_str)
            
        text_result = ""
        total_time = sum(distribution.values())
        for key, value in distribution.items():
            percentage = (value / total_time) * 100 if total_time else 0
            text_result += f"{key}: {value} minutes ({percentage:.2f}%)\n"

        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text_result)
        self.results_text.config(state='disabled')
        
        chart_type = self.chart_type_combobox.get()
        if self.show_graph_var.get():
            if chart_type == "Pie Chart":
                self.logs_and_analytics.display_pie_chart(distribution)
            elif chart_type == "Bar Chart":
                self.logs_and_analytics.display_bar_chart(distribution)
            elif chart_type == "Line Chart":
                daily_distribution = self.logs_and_analytics.get_daily_study_times(selected_courses, selected_tasks, start_date, end_date)
                self.logs_and_analytics.display_line_chart(daily_distribution)

    def export_to_csv(self):
        selected_courses, start_date, end_date = self.validate_courses_and_dates()
        if selected_courses is None or start_date is None or end_date is None: return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        start_date = datetime.strptime(self.start_date_entry.get(), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(self.end_date_entry.get(), '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')

        query = 'SELECT * FROM StudySessions WHERE courseID IN ({}) AND start_time >= ? AND end_time <= ?'
        query = query.format(','.join('?' for _ in self.analytics_course_listbox.curselection()))
        params = [start_date, end_date]
        params = [self.analytics_course_listbox.get(i) for i in self.analytics_course_listbox.curselection()] + params

        if self.analytics_task_listbox.curselection():
            query += ' AND taskID IN ({})'
            query = query.format(','.join('?' for _ in self.analytics_task_listbox.curselection()))
            params.extend([self.analytics_task_listbox.get(i) for i in self.analytics_task_listbox.curselection()])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            title="Save the file"
        )

        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([i[0] for i in cursor.description])
                writer.writerows(rows)

        conn.close()
