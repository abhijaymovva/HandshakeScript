
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def main():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    
    print(f"Page Title: {driver.title}")
    
    print("\n--- BUTTONS ---")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        if b.is_displayed():
            print(f"TEXT: '{b.text}' | HTML: {b.get_attribute('outerHTML')[:100]}...")

    print("\n--- INPUTS TYPE=SUBMIT ---")
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
    for i in inputs:
        if i.is_displayed():
            print(f"VALUE: '{i.get_attribute('value')}' | HTML: {i.get_attribute('outerHTML')[:100]}...")

    print("\n--- TASKS/DIVS THAT LOOK LIKE BUTTONS ---")
    # Sometimes buttons are divs with role=button
    divs = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
    for d in divs:
        if d.is_displayed():
             print(f"TEXT: '{d.text}' | CLASS: {d.get_attribute('class')}")

if __name__ == "__main__":
    main()
