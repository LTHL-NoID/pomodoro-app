# Focus Flow - Pomodoro To-Do App

**Focus Flow** is a desktop application that combines the Pomodoro Technique with a task management system. It helps users manage focus sessions, track tasks, earn points for completed tasks, and monitor productivity over time.

This version adds fully customizable Pomodoro and break durations, improved task editing, multi-line tasks with points, drag-and-drop ordering, and undo functionality for task deletion.

---

## Features

- **Pomodoro Timer**
  - Standard 25-minute focus sessions with 5-minute breaks
  - Long break of 30 minutes after 4 sessions
  - Fully **customizable focus and break times**
  - Visual timer with color indicators:
    - Green: Focus
    - Blue: Break
    - Red: Warning when time is almost up
  - Sound alerts at the end of each session
  - Automatic session tracking and streak monitoring

- **Task Management**
  - Add, edit, and delete tasks
  - Multi-line task descriptions
  - Assign points to tasks
  - Toggle completion with single click
  - Double click to edit task text or points
  - Drag-and-drop to reorder tasks
  - Undo last deleted task with Ctrl + Z

- **Statistics**
  - Track total focus time, sessions, and streaks
  - Daily overview with task scores
  - Points gained/lost when marking tasks complete/incomplete

- **Instructions & Motivational Quotes**
  - Built-in guidance for first-time users
  - Random motivational quotes displayed after each session

---

## Installation

1. Clone or download the repository:

    ```bash
    git clone https://github.com/LTHL-NoID/pomodoro-app.git
    ```

2. Install dependencies:

    ```bash
    pip install pygame-ce==2.5.6
    ```

3. Ensure the following directory structure exists:

    ```text
    pomodoro-app/
    ├─ media/
    │  ├─ images/          # App icons
    │  ├─ alarms/          # Optional sound files (.wav, .mp3, .ogg)
    │  └─ music/           # Future mp3 playback support
    ├─ cfg/                # Automatically created on first run
    └─ focus.py            # Main app file
    ```

---

## Usage

Run the app:

```bash
python3 focus.py
```

---

## Controls

- **Start / Stop**: Begin or pause the Pomodoro timer
- **Custom Timer**: Set custom focus and break durations
- **Add Task**: Create a new task with points
- **Task Checkboxes**: Single click to toggle completion
- **Edit Task**: Double click task to edit text and points
- **Delete Task**: Right-click to remove task
- **Drag-and-Drop**: Reorder tasks by dragging
- **Undo**: Ctrl + Z to restore the last deleted task
- **Instructions**: View app guidance
- **Statistics**: View focus time, sessions, and points

---

## File Structure

- `focus.py` – Main application code
- `cfg/state.json` – Saved tasks
- `cfg/config.json` – Custom session/break durations
- `cfg/stats.json` – User statistics
- `media/images/` – App icons
- `media/alarms/` – Optional sound alarms for sessions

---

## Dependencies

- **Python 3** – https://www.python.org/
- **Pygame** – https://www.pygame.org/
- **Tkinter** – https://docs.python.org/3/library/tkinter.html

---

## Known Bugs / Notes

- ~~After setting custom timer durations, you may need to click **Start** twice to begin the timer.~~ Fixed
- ~~Task drag-and-drop may require precise mouse movements to reorder correctly.~~
- ~~No visual task drag-and-drop~~

---

## Future Improvements

- Add background music during sessions
- Sync statistics across devices
- Mobile or web version

