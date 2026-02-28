# Handshake AI Task Automation

This script automates the submission process for Handshake AI tasks ("omni-tts-elo"). It runs in an infinite loop, performing tasks every 55 minutes.

## Prerequisites

1.  **Python 3.13+** installed.
2.  **Google Chrome** installed.

## Setup

1.  Create and activate a virtual environment (optional but recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  Install dependencies:
    ```bash
    pip install selenium
    ```

## Usage

### Step 1: Launch Chrome with Remote Debugging

You have two options:

**Option A: Use your Main Profile (Recommended so you stay logged in)**
1.  **Quit ALL running Chrome instances** (Command + Q). This is critical.
2.  Run this in your terminal:
    ```bash
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
    ```

**Option B: Use a Temporary Profile (Clean slate)**
If Option A causes issues, use this command to start a fresh, temporary instance. Note: You will lose your profiles *in this window only* and have to log in again.
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev_test"
```

### Step 2: Log In

1.  In the new Chrome window that opens, navigate to `https://ai.joinhandshake.com/`.
2.  Log in to your account.
3.  Navigate to the "Task List" page where the `260209-omni-tts-elo` button is visible.

### Step 3: Run the Script

Open a new terminal window (keep the Chrome terminal open), navigate to this folder, and run:

```bash
source .venv/bin/activate  # If using venv
python handshake_submit.py
```

## What the Script Does

1.  **Starts Loop**: Connects to your open Chrome window.
2.  **Selects Task**: Clicks "omni-tts-elo".
3.  **Waits**: Starts a **1-minute countdown**.
4.  **Submits**: Clicks "Submit" immediately after the wait.
5.  **Resets**: Clicks "Next Task", "Open Multimango", closes the popup tab, and restarts the cycle.

## Troubleshooting

*   **"Connection refused"**: Make sure Chrome was started with `--remote-debugging-port=9222` and is still running.
*   **"Element not found"**: Ensure you are on the correct page. If the UI changes (button text, etc.), the script may need updating.
*   **Wait time**: The wait duration is set to 1 minute by default. You can change this in `handshake_submit.py` by editing `TASK_DURATION_MINUTES`.
