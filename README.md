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

You must launch Chrome from the terminal with a specific flag so the script can control it.

**Close all existing Chrome windows completely first.**

Run this command in your terminal:
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
3.  **Fills Form**:
    *   Fills the first text box with `X`.
    *   Clicks "Submit" / "Save".
    *   Fills subsequent text boxes with `0`.
    *   Clicks "Submit" / "Save" after each one.
4.  **Waits**: Once all fields are done and the final submission is complete, it starts a **55-minute countdown**.
5.  **Resets**: After the wait, it clicks "Next Task", "Open Multimango", closes the popup tab, and restarts the cycle.

## Troubleshooting

*   **"Connection refused"**: Make sure Chrome was started with `--remote-debugging-port=9222` and is still running.
*   **"Element not found"**: Ensure you are on the correct page. If the UI changes (button text, etc.), the script may need updating.
*   **Stuck on "Waiting for input"**: Click inside the input box manually to help it along if it gets stuck.
