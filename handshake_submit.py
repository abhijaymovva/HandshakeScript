"""
Handshake AI Task Submission Automation
========================================
Prerequisites:
  1. pip install selenium
  2. Launch Chrome with remote debugging
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
MENU_OPTION = "260209-omni-tts-elo"
FIRST_FIELD_VALUE = "X"
REMAINING_FIELDS_VALUE = "0"
REMAINING_FIELDS_COUNT = 5
WAIT_TIMEOUT = 20
MIN_DELAY = 7
MAX_DELAY = 7
TASK_DURATION_MINUTES = 50  # Global variable for the long wait
# ────────────────────────────────────────────────────────


def human_delay(context=""):
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"    ⏳ Waiting {delay:.1f}s{' (' + context + ')' if context else ''}...")
    time.sleep(delay)


def human_type(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))


def connect_to_chrome():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[✓] Connected to Chrome")
        return driver
    except Exception as e:
        print(f"[✗] Could not connect to Chrome: {e}")
        sys.exit(1)


def click_task_button(driver, wait, option_text):
    """Click a task button by its exact text."""
    print(f"\n[1] Clicking task button '{option_text}'...")
    try:
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//button[normalize-space(text())='{option_text}']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)
        btn.click()
        print(f"    [✓] Clicked '{option_text}'")
        return True
    except Exception as e:
        print(f"    [✗] Could not find button '{option_text}': {e}")
        return False


def find_and_click_save(driver):
    """Find and click a Save/Submit button."""
    print(f"    Looking for Save/Submit button...")

    # Expanded list of probable button texts
    targets = ["Save", "Submit", "Next", "Confirm", "OK", "Done", "Continue", "submit", "save"]
    
    # 1. Try generic text match (case-insensitive partial match for safety)
    try:
        # Get all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        # Filter for visible and enabled
        visible_buttons = [b for b in buttons if b.is_displayed() and b.is_enabled()]
        
        # Check against our target list
        for target in targets:
            for btn in visible_buttons:
                # Check text OR aria-label
                btn_text = btn.text.strip().lower()
                btn_aria = btn.get_attribute("aria-label")
                if btn_aria:
                    btn_aria = btn_aria.strip().lower()
                else:
                    btn_aria = ""

                if target.lower() in btn_text or target.lower() in btn_aria:
                    found_via = "text" if target.lower() in btn_text else "aria-label"
                    print(f"    [✓] Found button '{target}' via {found_via}")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.5)
                    btn.click()
                    return True
    except Exception as e:
        print(f"    [!] Error searching buttons by text: {e}")

    # 2. Fallback: type=submit
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        visible = [b for b in buttons if b.is_displayed() and b.is_enabled()]
        if visible:
            visible[-1].click()
            print(f"    [✓] Clicked submit button (fallback css)")
            time.sleep(1)
            return True
    except Exception:
        pass

    print(f"    [!] No Save/Submit button found among {len(visible_buttons) if 'visible_buttons' in locals() else '?'} visible buttons")
    if 'visible_buttons' in locals():
         for b in visible_buttons[:5]:
             print(f"       - Available: '{b.text.strip()}'")
    return False


def wait_for_input_field(driver, timeout=20):
    """Wait for a text input field to appear on the page."""
    print(f"    Waiting for input field...")
    selectors = "input[type='text'], input[type='number'], input:not([type]), textarea"

    for attempt in range(timeout):
        inputs = driver.find_elements(By.CSS_SELECTOR, selectors)
        visible = [i for i in inputs if i.is_displayed() and i.is_enabled()]
        if visible:
            print(f"    [✓] Found input field")
            return visible[0]
        time.sleep(1)

    print(f"    [!] No input field found after {timeout}s")
    return None


def click_button_by_text(driver, text, timeout=15):
    """Click a button by its exact visible text. Waits for it to appear."""
    print(f"    Looking for '{text}' button...")
    wait = WebDriverWait(driver, timeout)
    try:
        # Check text exact match
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//button[normalize-space(text())='{text}']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5)
        btn.click()
        print(f"    [✓] Clicked '{text}' (exact text)")
        time.sleep(0.5)
        return True
    except Exception:
        # Check aria-label exact match
        try:
             # Case-insensitive aria-label match just in case
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//button[@aria-label='{text}']")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print(f"    [✓] Clicked '{text}' (aria-label)")
            time.sleep(0.5)
            return True
        except Exception:
            pass

        # Also try partial match
        try:
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//button[contains(normalize-space(text()),'{text}')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.5)
            btn.click()
            print(f"    [✓] Clicked button containing '{text}'")
            time.sleep(0.5)
            return True
        except Exception:
            pass
    print(f"    [!] Could not find '{text}' button")
    return False


def close_current_tab(driver):
    """Close the current tab (new tab opened by Multimango) and switch back."""
    print(f"    Closing new tab...")
    handles = driver.window_handles
    if len(handles) > 1:
        # We're on the new tab — close it
        driver.close()
        # Switch back to the original tab
        driver.switch_to.window(driver.window_handles[0])
        print(f"    [✓] Closed tab, back to: {driver.title}")
    else:
        # Only one tab, use Cmd+W as fallback
        ActionChains(driver).key_down(Keys.COMMAND).send_keys('w').key_up(Keys.COMMAND).perform()
        print(f"    [✓] Sent Cmd+W")
        time.sleep(1)


def debug_page(driver):
    """Print page state for debugging."""
    print(f"    --- Page: {driver.title} ---")
    btns = driver.find_elements(By.TAG_NAME, "button")
    vis_btns = [b for b in btns if b.is_displayed() and b.text.strip()]
    print(f"    Visible buttons: {len(vis_btns)}")
    for b in vis_btns[:8]:
        print(f"      - '{b.text.strip()[:60]}'")
    inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea")
    vis_in = [i for i in inputs if i.is_displayed()]
    print(f"    Visible inputs: {len(vis_in)}")


def wait_for_save_button_to_enable(driver, timeout=20):
    """Wait for a visible Save/Submit button to become enabled (clickable)."""
    print(f"    Waiting for Save/Submit button to become active...")
    end_time = time.time() + timeout
    
    # Common text for the button
    targets = ["Save", "Submit", "Next", "Confirm", "OK", "Done", "Continue", "submit", "save"]

    while time.time() < end_time:
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            # Filter for visible
            visible = [b for b in buttons if b.is_displayed()]
            
            # Find matching button
            target_btn = None
            for b in visible:
                b_text = b.text.strip().lower()
                b_aria = b.get_attribute("aria-label") or ""
                if any(t.lower() in b_text or t.lower() in b_aria.lower() for t in targets):
                    target_btn = b
                    break
            
            if target_btn:
                if target_btn.is_enabled():
                    print(f"    [✓] Button '{target_btn.text or 'Icon'}' is active.")
                    return target_btn
                else:
                    # Still disabled, wait
                    time.sleep(0.5)
                    continue
            
            # If no button found at all, wait
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
            
    print(f"    [!] Timed out waiting for button to enable.")
    return None

def main():
    print("=" * 50)
    print("  Handshake AI Task Submission (Infinite Loop)")
    print("=" * 50)

    driver = connect_to_chrome()
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    while True:  # Infinite loop
        print(f"\n[0] Current page: {driver.title}")

        # Step 0.5: Click 'Continue' on the 'Estimated Time' page (Before selecting task)
        print(f"\n[0.5] Looking for 'Continue' button (Estimated Time page)...")
        if click_button_by_text(driver, "Continue", timeout=5):
             human_delay("after clicking Continue")
        else:
             print("    [!] 'Continue' button not found (might be skipped or already passed).")

        # Step 1: Click the task option button
        # (This moves us to the intermediate screen)
        click_task_button(driver, wait, MENU_OPTION)
        
        human_delay("after selecting task")
        
        # Check if we need to click Continue/Submit again here (intermediate page)
        print(f"    Looking for intermediate Submit/Continue button...")
        
        # 1. Try 'Submit' button
        if click_button_by_text(driver, "Submit", timeout=5):
             human_delay("after intermediate Submit")
        
        # 2. Try 'Continue' button (often the case)
        elif click_button_by_text(driver, "Continue", timeout=2):
             human_delay("after intermediate Continue")
        
        # 3. Try to find *any* clickable element with explicit text 'Submit'
        else:
             print("    [!] Standard button search failed. Trying deep search for 'Submit'...")
             try:
                 submit_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                     (By.XPATH, "//*[normalize-space(text())='Submit']")
                 ))
                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                 time.sleep(0.5)
                 submit_btn.click()
                 print("    [✓] Clicked generic element with text 'Submit'")
                 human_delay("after generic Submit")
             except:
                 print("    [!] No intermediate button found. Assuming direct entry.")

        # Try Save if it exists (sometimes 'Save' appears early)
        save_found = find_and_click_save(driver)
        if save_found:
             human_delay("after initial Save")

        # Step 2: Loop until no more input fields found or Submit appears
        print(f"\n{'='*40}")
        print(f"[Step 2] Filling fields until done...")
        print(f"{'='*40}")

        step = 1
        while True:
            # Check if final Submit is available right away (e.g. no more inputs)
            # But be careful, sometimes Submit is visible but disabled, or visible at bottom always.
            # Usually input field appears first.
            
            human_delay(f"before checking for input {step}")
            
            # Wait longer for loading (increased from 10s to 45s due to slow app response)
            print(f"    ⏳ Waiting for next input field (up to 45s)...")
            field = wait_for_input_field(driver, timeout=45)
            
            if not field:
                # Double check: Is the "Submit" button present?
                # If "Submit" is present, we are truly done. 
                # If neither field nor Submit is present, we might just be loading very slowly.
                print(f"    [!] Input field not found. checking for Final Submit button...")
                is_submit_present = False
                try:
                    # Look specifically for the FINAL submit button, not the intermediate Save
                    sub_btns = driver.find_elements(By.XPATH, "//button[normalize-space(text())='Submit']")
                    if any(b.is_displayed() for b in sub_btns):
                         is_submit_present = True
                except:
                    pass

                if is_submit_present:
                     print(f"    [✓] Final Submit button detected. Proceeding to wait period.")
                     break
                else:
                     print(f"    [!] Neither Input Field nor Submit button found. Retrying wait...")
                     time.sleep(5)
                     field = wait_for_input_field(driver, timeout=20)
                     if not field:
                         print(f"    [!] Still no field. Assuming end of task.")
                         break

            value = FIRST_FIELD_VALUE if step == 1 else "0"
            print(f"\n    --- Field {step} found. Typing '{value}' ---")

            # Type the value
            try:
                field.click()
                time.sleep(random.uniform(0.3, 0.8))
                field.clear()
                time.sleep(random.uniform(0.2, 0.5))
                human_type(field, value)
                print(f"    [✓] Typed '{value}'")
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                print(f"    [!] Error with field: {e}")
                break

            # Click Save/Next
            save_clicked = False
            
            # Wait for the button to become enabled *after* typing
            active_btn = wait_for_save_button_to_enable(driver, timeout=10)
            
            if active_btn:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", active_btn)
                    time.sleep(0.3)
                    active_btn.click()
                    print(f"    [✓] Clicked Save/Submit button")
                    save_clicked = True
                    save_found_element = active_btn
                except Exception as e:
                    print(f"    [!] Failed to click Save: {e}")
            
            if not save_clicked:
                # Fallback search
                print(f"    [!] Looking for button with broader search...")
                if find_and_click_save(driver):
                    save_clicked = True
                else:    
                    print(f"    [!] Could not click Save. Checking if we are done...")
                    break
            
            # ────────────────────────────────────────────────────────
            # TEMPLATE MATCHING / STATE CHANGE DETECTION
            # ────────────────────────────────────────────────────────
            print(f"    ⏳ Waiting for state change (old field to disappear)...")
            
            try:
                # 1. Wait for the OLD input field to become stale (removed from DOM)
                WebDriverWait(driver, 20).until(EC.staleness_of(field))
                print(f"       [✓] Old input field removed.")
            except Exception:
                print(f"       [!] Warning: Old field did not disappear (might be reused).")

            step += 1

        # LONG WAIT before Step 3 (Final Submit)
        duration_sec = TASK_DURATION_MINUTES * 60
        print(f"\n{'='*40}")
        print(f"[WAIT] Sleeping for {TASK_DURATION_MINUTES} minutes before FINAL SUBMIT...")
        print(f"{'='*40}")
        # Countdown
        for remaining in range(duration_sec, 0, -10):
            sys.stdout.write(f"\r    ⏳ Submitting in {remaining}s...   ")
            sys.stdout.flush()
            time.sleep(10)
        print("\n    [✓] Resuming...")

        # Step 3: Click the Submit button at the bottom
        print(f"\n{'='*40}")
        print(f"[Step 3] Clicking Submit button")
        print(f"{'='*40}")
        human_delay("before Submit")
        click_button_by_text(driver, "Submit")
        
        # Step 4: Popup "Great job! Ready for another task?" → Click "Next task"
        print(f"\n{'='*40}")
        print(f"[Step 4] Clicking 'Next task' in popup")
        print(f"{'='*40}")
        human_delay("before Next task")
        # Retry logic in case the popup took a while or we timed out
        if not click_button_by_text(driver, "Next task"):
             print("    [!] 'Next task' not found, trying generic search...")

        # Step 5: Popup "Start task" → Click "Open Multimango"
        print(f"\n{'='*40}")
        print(f"[Step 5] Clicking 'Open Multimango'")
        print(f"{'='*40}")
        human_delay("before Open Multimango")
        click_button_by_text(driver, "Open Multimango")

        # Step 6: Close the new tab that opened
        print(f"\n{'='*40}")
        print(f"[Step 6] Closing new tab")
        print(f"{'='*40}")
        time.sleep(5)  # Increased wait to let tab load fully
        
        # Switch to newest tab
        handles = driver.window_handles
        if len(handles) > 1:
            driver.switch_to.window(handles[-1])
            print(f"    Switched to new tab: {driver.title}")
            time.sleep(1)
            driver.close()
            # Switch back to original
            driver.switch_to.window(handles[0])
            print(f"    [✓] Closed tab, back to: {driver.title}")
        else:
            print("    [!] No new tab detected.")

        print("\n" + "=" * 50)
        print("  [✓] Cycle complete. Restarting loop...")
        print("=" * 50)
        time.sleep(5) # Short cool-down before restarting loopl done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
