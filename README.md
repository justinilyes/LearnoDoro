<h1 align="center" style="font-weight: bold;"> LearnoDoro </h1>
<h2 align="center" style="font-weight: bold;"> The Pomodoro Timer App for Students </h2>

<p align="center">
<img src="docs/LearnoDoroLogo1.png" alt="LearnoDoro Logo" width="200"/>
</p>

For the everyday student grinding through lectures, assignments, and group projects, who struggles with time management and seeks tangible proof of their dedication, LearnoDoro is the solution. It offers a customized study regiment enriched by insightful feedback. While numerous other timer apps exist, most offer just basic timer functionality and miss out on the analytics on how your time is spent. LearnoDoro ensures that students (and whoever finds good use of it) gain a comprehensive overview of precisely how their study hours are allocated.

## **What even is Pomodoro?**

The Pomodoro Technique is a time management method that involves working in focused 25-minute intervals (called "Pomodoros") followed by short breaks to improve productivity and concentration.

### **The Pomodoro Process**

1. Choose task to do
2. Set Pomodoro timer (usually 25 min)
3. Do the task until the timer reaches 0
4. take a short break (ca. 5–10 min)
5. Return to Step 2 and repeat until four pomodoros are completed
6. After four pomodoros, take a long break (ca. 20-30 min) instead of a short break
7. Return to step 2

## **Core Features**

1) Pomodoro Timer
   - Users select a "Course" at the start of each Pomodoro. Optionally, they may choose a specific "Task" within that course
   - Start/Stop the countdown timer
   - Settings to customize study time duration, short break length, long break length and the number of Pomodoros required before a long break

2) Courses
   - Create a "Course"
   - Create a "Task" within a "Course"
   - Time spent working on a specific "Course" is logged

3) Tasks
   - Create a "Task" in a "Course"
   - Time spent working on a specific "Task" is logged too

4) Logs and Analytics
   - Logs each "StudySession" spent on each "Course" and "Task"
   - Comparative Analysis across "Courses" and "Tasks"
   - View study time over selected time-periods
   - Visual Representations like bar graphs, pie charts and line charts for easy understanding
   - Export "StudySessions" to .csv for further analysis

## **Installation and Setup**

LearnoDoro offers two convenient methods for installation and setup:

Using `main.py`:

- Edit config.py in the /Software directory to set your database save location.
- In DEVELOPMENT mode (DEVELOPMENT = True), database and settings are stored in /Software/data.
- In production mode (DEVELOPMENT = False), database and settings are stored in the user's local appdata.

Using `main.exe`:

- No code modifications required.
- All data is automatically saved in the user's local appdata.

Once setup is complete, LearnoDoro is ready for use. Happy studying!

## **Usage Instructions**

Simplicity is key in LearnoDoro, ensuring you spend more time studying and less figuring out the app.

Here's your quick guide to get started:

1. Launch LearnoDoro
2. Add a Course: First-timers, add a new course. Or, select an existing course from the dropdown next to `Add Course`.
3. Add a Task (Optional): You can add a new task to your course or choose an existing one from the dropdown next to `Add Task`.
4. Check Settings (Optional): Go to `Settings` to adjust the timer to your preference. Default settings follow the traditional Pomodoro technique.
5. Start Studying: Set your course, task (optional), and timer settings, then hit `Start` to begin your study session.
6. Follow the Timer: Study and take breaks as indicated by the timer.
7. Stop and Log: Once done, click `Stop`. Your session will be logged and viewable in `Analytics`.

Using Analytics:

1. Access Analytics: Go to `Analytics` for a session overview. A new window will open.
2. Select Courses/Tasks: Choose the courses and tasks you want insights on.
3. Set Date Range: Enter the start and end dates as per the format shown in the window.
4. View Charts (Optional): To see a chart, click `Show Graph` and choose the chart type.
5. Display Analytics: Click `Display Analytics` to view your study data.
6. Export Logs (Optional): To download study logs for the selected period, click `Export Study Logs to CSV`.

## **Dependencies**

| Dependency | Reason for inclusion |
|:----------:|:---------------------|
|  `ttkthemes`  | App GUI |
|  `matplotlib`  | Visualize the data (pie,bar,line charts) |
|  `pytest`  | Testing implementations in this project using automatic test cases. |
