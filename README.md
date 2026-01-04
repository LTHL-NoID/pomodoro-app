# Focus Flow - Pomodoro To-Do App

**Focus Flow** is a desktop application that combines the Pomodoro Technique with a task management system. It helps users manage their focus sessions, track tasks, and earn points for completing tasks while monitoring their productivity over time.

---

## Features

- **Pomodoro Timer**
  - Standard 25-minute focus sessions with 5-minute breaks
  - Long break of 30 minutes after 4 sessions
  - Custom timer option for flexible session lengths
  - Visual timer display with color indicators:
    - Green: Focus mode
    - Blue: Break
    - Red: Warning when time is almost up

- **Task Management**
  - Add, edit, and delete tasks
  - Multi-line task support
  - Assign points to tasks
  - Single click checkbox to mark task complete/incomplete
  - Double click to edit task text or points
  - Drag-and-drop to reorder tasks
  - Undo last deleted task

- **Statistics**
  - Track total focus time, sessions completed, and streaks
  - Daily performance overview with task scores
  - Earn or lose points based on task completion

- **Instructions and Motivational Quotes**
  - Built-in instructions guide for first-time users
  - Random motivational quotes displayed after session completion
  - Sound alerts at the end of each Pomodoro session

---

## Installation

1. Clone or download this repository:

    ```git clone https://github.com/LTHL-NoID/pomodoro-app.git```

2. Install dependencies:

    ```pip install pygame-ce==2.5.6```

3. Ensure the following directory structure exists:

    ```bash
    pomodoro-app/
    ├─ media/
    │  ├─ images/          # App icons
    │  ├─ alarms/          # Optional: sound files (.wav, .mp3, .ogg)
    |  └─ music/           # Future plans to allow mp3 playback
    ├─ cfg/                # Created automatically on first run
    └─ focus.py            # Main app file```

## Usage

python3 focus.py

## Controls

 - Start / Stop: Begin or pause the Pomodoro timer
 - Custom Timer: Set a custom session duration
 - Add Task: Add a new task with points
 - Task Checkboxes: Single click to toggle completion
 - Edit Task: Double click a task to edit text and points
 - Delete Task: Right-click a task to remove it
 - Drag and Drop: Reorder tasks by dragging
 - Undo: Press Ctrl + Z to restore the last deleted task
 - Instructions: View guidance on using the app
 - Statistics: View focus time, sessions, and points

## File Structure
 - `focus.py.py`     - Main application code
 - `cfg/state.json`  - Saved tasks
 - `cfg/stats.json`  - User statistics
 - `media/images/`   - App icons
 - `media/alarms/`   - Option sound alarms for sessions. Can just place .wav .mp3 .ogg audio files in here and they will be randomly used.

## Dependencies
 - Python3 - https://www.python.org/                            - Programming language
 - Pygame  - https://www.pygame.org/news                        - For UI rendering and sound
 - TKinter - https://docs.python.org/3/library/tkinter.html     - For dialogs and prompts

## Known bugs
 - After setting custom time, you need to click start twice to begin timer - If someone ever works this quirk out let me know its doing my head in.