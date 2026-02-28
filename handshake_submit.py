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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ──────────────────── CONFIGURATION ────────────────────
MENU_OPTION = "260209-omni-elo"
WAIT_TIMEOUT = 5
TASK_DURATION_MINUTES = 55
# ────────────────────────────────────────────────────────


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
    wait = WebDriverWait(driver, timeout)

    # 1. Exact text match
    try:
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
        xpath = f"//{tag}[contains(normalize-space(text()),'{text}')]"
        el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
        el.click()
        return True
    except Exception:
        pass

    # 3. Any element (not just <button>) — JS click as last resort
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


def main():
    print("=" * 50)
    print("  Handshake AI Task Submission")
    print("=" * 50)

    driver = connect_to_chrome()
    
    # Find the actual Handshake tab by checking all window handles
    original_handle = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url
        title = driver.title
        print(f"    Tab: {handle} — {title} ({url})")
        if "handshake" in url.lower() or "handshake" in title.lower():
            original_handle = handle
            print(f"    [✓] Found Handshake tab: {handle}")
    
    # If no handshake tab found, pick the first non-chrome:// tab
    if not original_handle:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            url = driver.current_url
            if not url.startswith("chrome://"):
                original_handle = handle
                print(f"    [✓] Using non-chrome tab: {handle} ({url})")
                break
    
    # Last resort: just use the first handle
    if not original_handle:
        original_handle = driver.window_handles[0]
        print(f"    [!] Falling back to first tab: {original_handle}")
    
    driver.switch_to.window(original_handle)
    print(f"    Active tab: {driver.title} — {driver.current_url}")

    while True:
        print(f"\n{'='*50}")
        print(f"  Starting new cycle...")
        print(f"{'='*50}")
        # Always make sure we're on the original Handshake tab
        driver.switch_to.window(original_handle)
        print(f"  Page: {driver.title}")
        print(f"  URL:  {driver.current_url}")
        
        # Switch out of any iframes back to main page content
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
                print(f"    [✗] Still can't find it. Will retry next cycle.")
                time.sleep(10)
                continue

        time.sleep(2)

        # ── Step 1b: Click the intermediate submit button (small arrow icon, bottom-right) ──
        print(f"\n[Step 1b] Looking for intermediate submit button...")
        time.sleep(2)
        found_intermediate = False

        # Try by aria-label (icon button with hover tooltip "Submit")
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

        # Fallback: try by visible text
        if not found_intermediate:
            for label in ["Submit", "Continue", "Next", "Save"]:
                if click_element_by_text(driver, label, timeout=3):
                    print(f"    [✓] Clicked intermediate '{label}' (text).")
                    found_intermediate = True
                    break

        # Last resort: try type=submit
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
        if click_element_by_text(driver, "Submit"):
            print(f"    [✓] Submitted.")
        else:
            print(f"    [✗] Could not find Submit button.")
        time.sleep(2)

        # ── Step 4: Click "Next task" ──
        print(f"\n[Step 4] Clicking 'Next task'...")
        if click_element_by_text(driver, "Next task", timeout=10):
            print(f"    [✓] Clicked 'Next task'.")
        else:
            print(f"    [✗] 'Next task' not found.")
        time.sleep(2)

        # ── Step 5: Click "Open Multimango" ──
        print(f"\n[Step 5] Clicking 'Open Multimango'...")
        if click_element_by_text(driver, "Open Multimango", timeout=10):
            print(f"    [✓] Clicked 'Open Multimango'.")
        else:
            print(f"    [✗] 'Open Multimango' not found.")
        time.sleep(3)

        # ── Step 6: Close the popup tab and switch back to original Handshake tab ──
        print(f"\n[Step 6] Closing popup tab...")
        close_newest_tab(driver, original_handle)

        print(f"\n[✓] Cycle complete.\n")
        time.sleep(3)


if __name__ == "__main__":
    main()
