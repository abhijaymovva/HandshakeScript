"""
Handshake AI Task Submission Automation
========================================
Prerequisites:
  1. pip install selenium
  2. Launch Chrome with remote debugging (port 9222)
  3. Log in and navigate to the task page
  4. Run: python handshake_submit.py
"""

import time
import sys
import random
import datetime

# Try to use zoneinfo (Python 3.9+), fall back to pytz
try:
    from zoneinfo import ZoneInfo
    CST = ZoneInfo("America/Chicago")
except (ImportError, Exception):
    import pytz
    CST = pytz.timezone("America/Chicago")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ──────────────────── CONFIGURATION ────────────────────
MENU_OPTION = "260209-omni-elo"
WAIT_TIMEOUT = 2
TASK_DURATION_MINUTES = 55
TASKS_PER_DAY = 14
# ────────────────────────────────────────────────────────


def tasks_remaining_today() -> int:
    """
    Calculate how many TASK_DURATION_MINUTES tasks fit between now and the
    next 1:00 AM CST cutoff, capped at TASKS_PER_DAY.
    """
    now = datetime.datetime.now(tz=CST)
    cutoff = now.replace(hour=1, minute=0, second=0, microsecond=0)
    # If 1 AM today is already past, the next cutoff is 1 AM tomorrow
    if cutoff <= now:
        cutoff += datetime.timedelta(days=1)
    minutes_left = (cutoff - now).total_seconds() / 60
    return min(TASKS_PER_DAY, int(minutes_left // TASK_DURATION_MINUTES))


def get_next_start_time() -> datetime.datetime:
    """
    Return a random start time between 12:00 PM and 12:30 PM CST.
    If that window has already passed today, schedule for tomorrow.
    """
    now = datetime.datetime.now(tz=CST)
    offset_minutes = random.randint(0, 29)
    offset_seconds = random.randint(0, 59)

    candidate = now.replace(
        hour=12, minute=offset_minutes, second=offset_seconds, microsecond=0
    )

    # Use today's candidate only if it's still in the future
    if candidate > now:
        return candidate

    # Otherwise push to tomorrow
    tomorrow = now.date() + datetime.timedelta(days=1)
    return datetime.datetime(
        tomorrow.year, tomorrow.month, tomorrow.day,
        12, offset_minutes, offset_seconds,
        tzinfo=CST,
    )


def wait_until(start_dt: datetime.datetime) -> None:
    """Sleep until start_dt, printing a progress line every minute."""
    now = datetime.datetime.now(tz=CST)
    wait_secs = (start_dt - now).total_seconds()
    if wait_secs <= 0:
        return

    print(
        f"\n[SCHEDULE] Next session starts at: "
        f"{start_dt.strftime('%Y-%m-%d %I:%M:%S %p %Z')}"
    )
    hrs, rem = divmod(int(wait_secs), 3600)
    mins = rem // 60
    print(f"[SCHEDULE] Waiting {hrs}h {mins}m ({int(wait_secs)}s)...")

    CHUNK = 60  # update display every 60 s
    while True:
        now = datetime.datetime.now(tz=CST)
        remaining = (start_dt - now).total_seconds()
        if remaining <= 0:
            break
        sleep_for = min(CHUNK, remaining)
        time.sleep(sleep_for)
        remaining -= sleep_for
        if remaining > 0:
            hrs, rem = divmod(int(remaining), 3600)
            mins = rem // 60
            sys.stdout.write(
                f"\r[SCHEDULE] Time until start: {hrs}h {mins}m remaining...   "
            )
            sys.stdout.flush()

    print("\n[SCHEDULE] Starting session now!")


def connect_to_chrome():
    """Connect to an already-running Chrome instance with remote debugging."""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[✓] Connected to Chrome — {driver.title}")
        return driver
    except Exception as e:
        print(f"[✗] Could not connect to Chrome: {e}")
        sys.exit(1)


def click_element_by_text(driver, text, tag="button", timeout=WAIT_TIMEOUT):
    """
    Wait for an element with the given text to be clickable, then click it.
    Falls back to partial match, then JS click if needed.
    Returns True if clicked, False otherwise.
    """
    # Use shorter timeouts for fallback strategies (half the main timeout, min 2s)
    fallback_timeout = max(2, timeout // 2)

    # 1. Exact text match
    try:
        wait = WebDriverWait(driver, timeout)
        xpath = f"//{tag}[normalize-space(text())='{text}']"
        el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
        el.click()
        return True
    except Exception:
        pass

    # 2. Partial / contains match
    try:
        wait = WebDriverWait(driver, fallback_timeout)
        xpath = f"//{tag}[contains(normalize-space(text()),'{text}')]"
        el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
        el.click()
        return True
    except Exception:
        pass

    # 3. Any element (not just <button>) — JS click as last resort (instant, no wait)
    try:
        xpath = f"//*[contains(normalize-space(text()),'{text}')]"
        els = driver.find_elements(By.XPATH, xpath)
        for el in els:
            if el.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", el)
                return True
    except Exception:
        pass

    return False


def close_newest_tab(driver, original_handle):
    """Close all tabs except the original Handshake tab, then switch back."""
    handles = driver.window_handles
    closed = 0
    if len(handles) > 1:
        for h in handles:
            if h != original_handle:
                driver.switch_to.window(h)
                url = driver.current_url
                # Skip chrome:// internal pages — they can't be closed
                if url.startswith("chrome://"):
                    continue
                tab_title = driver.title
                print(f"    Closing tab: {tab_title}")
                try:
                    # Use JS window.close() — works for tabs opened via links
                    driver.execute_script("window.close();")
                    closed += 1
                    time.sleep(0.5)
                except Exception:
                    # Fallback: try driver.close()
                    try:
                        driver.close()
                        closed += 1
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"    [!] Could not close tab '{tab_title}': {e}")
        driver.switch_to.window(original_handle)
        print(f"    [✓] Closed {closed} tab(s). Back to: {driver.title}")
    else:
        print("    [!] No new tab to close.")


def countdown(minutes):
    """Print a countdown timer for the given number of minutes."""
    total = minutes * 60
    print(f"\n[WAIT] Waiting {minutes} minute(s) before submitting...")
    for remaining in range(total, 0, -10):
        sys.stdout.write(f"\r    ⏳ {remaining}s remaining...   ")
        sys.stdout.flush()
        time.sleep(10)
    print(f"\r    [✓] Done waiting.              ")


def run_session(driver, original_handle, n_tasks: int) -> None:
    """Run n_tasks task cycles back-to-back."""
    print(f"\n{'='*50}")
    print(
        f"  Session — {n_tasks} task(s)  "
        f"(started {datetime.datetime.now(tz=CST).strftime('%I:%M %p %Z')})"
    )
    print(f"{'='*50}")

    for task_num in range(1, n_tasks + 1):
        print(f"\n{'='*50}")
        print(f"  Task {task_num}/{n_tasks}")
        print(f"{'='*50}")

        driver.switch_to.window(original_handle)
        print(f"  Page: {driver.title}")
        print(f"  URL:  {driver.current_url}")
        driver.switch_to.default_content()

        # ── Step 1: Click the task button ──
        print(f"\n[Step 1] Clicking '{MENU_OPTION}'...")
        if click_element_by_text(driver, MENU_OPTION):
            print(f"    [✓] Selected task.")
        else:
            print(f"    [✗] Could not find '{MENU_OPTION}'. Refreshing and retrying...")
            driver.refresh()
            time.sleep(5)
            if click_element_by_text(driver, MENU_OPTION):
                print(f"    [✓] Selected task after refresh.")
            else:
                print(f"    [✗] Still can't find it. Skipping this task.")
                time.sleep(10)
                continue

        time.sleep(2)

        # ── Step 1b: Click the intermediate submit button ──
        print(f"\n[Step 1b] Looking for intermediate submit button...")
        time.sleep(2)
        found_intermediate = False

        try:
            btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Submit'], button[title='Submit']")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.3)
            btn.click()
            print(f"    [✓] Clicked intermediate submit (aria-label/title).")
            found_intermediate = True
        except Exception:
            pass

        if not found_intermediate:
            for label in ["Submit", "Continue", "Next", "Save"]:
                if click_element_by_text(driver, label, timeout=3):
                    print(f"    [✓] Clicked intermediate '{label}' (text).")
                    found_intermediate = True
                    break

        if not found_intermediate:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                for btn in btns:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                        time.sleep(0.3)
                        btn.click()
                        print(f"    [✓] Clicked intermediate submit (type=submit).")
                        found_intermediate = True
                        break
            except Exception:
                pass

        if not found_intermediate:
            print(f"    [—] No intermediate button found (may not be needed).")

        # ── Step 2: Wait ──
        countdown(TASK_DURATION_MINUTES)

        # ── Step 3: Click Submit ──
        print(f"\n[Step 3] Clicking 'Submit'...")
        if click_element_by_text(driver, "Submit", timeout=5):
            print(f"    [✓] Submitted.")
        else:
            print(f"    [✗] Could not find Submit button.")
        time.sleep(2)

        # ── Step 4: Click 'Next task' ──
        print(f"\n[Step 4] Clicking 'Next task'...")
        if click_element_by_text(driver, "Next task", timeout=5):
            print(f"    [✓] Clicked 'Next task'.")
        else:
            print(f"    [✗] 'Next task' not found.")
        time.sleep(2)

        # ── Step 5: Click 'Open Multimango' ──
        print(f"\n[Step 5] Clicking 'Open Multimango'...")
        if click_element_by_text(driver, "Open Multimango", timeout=5):
            print(f"    [✓] Clicked 'Open Multimango'.")
        else:
            print(f"    [✗] 'Open Multimango' not found.")
        time.sleep(3)

        # ── Step 6: Close the popup tab and switch back ──
        print(f"\n[Step 6] Closing popup tab...")
        close_newest_tab(driver, original_handle)

        print(f"\n[✓] Task {task_num}/{n_tasks} complete.\n")
        time.sleep(3)

    print(
        f"\n{'='*50}\n"
        f"  [✓] Session complete — {n_tasks}/{n_tasks} tasks submitted."
        f"\n  Finished at: {datetime.datetime.now(tz=CST).strftime('%I:%M %p %Z')}"
        f"\n{'='*50}"
    )


def main():
    print("=" * 50)
    print("  Handshake AI Task Submission")
    print("=" * 50)

    driver = connect_to_chrome()
    time.sleep(1)  # Let Chrome stabilize after connecting
    
    # Find the tab that has the task button by scanning ALL tabs
    original_handle = None
    print(f"\n    Scanning {len(driver.window_handles)} open tab(s) for '{MENU_OPTION}'...")
    
    for i, handle in enumerate(driver.window_handles):
        driver.switch_to.window(handle)
        driver.switch_to.default_content()
        url = driver.current_url
        title = driver.title
        print(f"    [{i}] {title} — {url}")
        
        # Skip chrome:// internal pages
        if url.startswith("chrome://"):
            continue
        
        # Check if the task button is actually on this page
        try:
            driver.find_element(By.XPATH, f"//button[contains(text(),'{MENU_OPTION}')]")
            original_handle = handle
            print(f"    [✓] Found '{MENU_OPTION}' button on this tab!")
            break
        except Exception:
            # Button not on this page, also check by URL/title as backup
            if "handshake" in url.lower() or "handshake" in title.lower():
                original_handle = handle
                print(f"    [~] Handshake tab (button not visible yet, may need loading)")
                # Don't break — keep looking for a tab that actually has the button
    
    if not original_handle:
        print(f"\n    [!] No tab with '{MENU_OPTION}' or 'handshake' found.")
        print(f"    Falling back to first non-chrome:// tab...")
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if not driver.current_url.startswith("chrome://"):
                original_handle = handle
                print(f"    [✓] Using: {driver.title} ({driver.current_url})")
                break
    
    if not original_handle:
        print(f"\n    [!] ERROR: No usable tab found. Make sure Handshake is open.")
        sys.exit(1)
    
    driver.switch_to.window(original_handle)
    driver.switch_to.default_content()
    print(f"\n    Active tab: {driver.title}")
    print(f"    URL: {driver.current_url}")

    # ── First run: start immediately, only do as many tasks as fit before 1 AM ──
    n_today = tasks_remaining_today()
    now_cst = datetime.datetime.now(tz=CST)
    print(f"\n[SCHEDULE] Current time: {now_cst.strftime('%I:%M %p %Z')}")
    print(f"[SCHEDULE] Tasks that fit before 1:00 AM CST today: {n_today}")

    if n_today > 0:
        run_session(driver, original_handle, n_today)
    else:
        print("[SCHEDULE] No tasks fit before 1 AM — skipping to next noon window.")

    # ── Daily loop: wait for noon, run full 14 tasks, repeat ──
    while True:
        start_dt = get_next_start_time()
        wait_until(start_dt)
        run_session(driver, original_handle, TASKS_PER_DAY)


if __name__ == "__main__":
    main()
