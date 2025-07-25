import argparse
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def setup_driver():
    """Initialize and return a Chrome WebDriver with stealth options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-webrtc")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)

# --- Page Functions ---
def is_on_target_page(driver, target_url):
    return driver.current_url.startswith(target_url)

def get_scroll_position(driver):
    return driver.execute_script("return window.scrollY;")

def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def find_congrats_on_elements(driver):
    xpath = "//span[contains(text(), 'Congrats on')] | //div[contains(., 'Congrats on')]"
    return driver.find_elements(By.XPATH, xpath)

def click_and_send(driver, wait, target_url, element):
    try:
        if not is_on_target_page(driver, target_url):
            logging.warning("Navigated away from target. Aborting.")
            return

        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

        if not element.is_displayed() or not element.is_enabled():
            logging.debug("Element not interactable.")
            return

        try:
            clickable = element.find_element(By.XPATH, ".//button | .//a")
        except Exception:
            logging.debug("No clickable child found.")
            return

        if clickable.tag_name == "a":
            logging.info("Skipping link to avoid navigation.")
            return

        clickable.click()

        if not is_on_target_page(driver, target_url):
            logging.warning("Navigation occurred after click.")
            return

        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]")))
        time.sleep(0.5)
        send_btn.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Message sent')]")))
        logging.info("Message sent successfully.")
    except Exception as e:
        logging.error(f"Error handling element: {e}")

def process_elements(driver, target_url, wait):
    last_pos = 0
    while True:
        if not is_on_target_page(driver, target_url):
            break

        current_pos = get_scroll_position(driver)
        if current_pos > last_pos:
            logging.info("Detected user scroll. Searching for elements...")
            last_pos = current_pos

        elements = find_congrats_on_elements(driver)
        if not elements:
            logging.info("No 'Congrats on' found. Scrolling...")
            scroll_down(driver)
            continue

        for i, el in enumerate(elements):
            logging.info(f"Processing element {i + 1} of {len(elements)}")
            click_and_send(driver, wait, target_url, el)
            time.sleep(1)

        logging.info("Batch processed. Scrolling for more...")
        scroll_down(driver)

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="LinkedIn congrats message automation.")
    parser.add_argument("--url", default="https://www.linkedin.com/mynetwork/catch-up/all/", help="Target LinkedIn URL")
    parser.add_argument("--auto", action="store_true", help="Start process without prompt")
    args = parser.parse_args()

    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(args.url)
        if args.auto or input("Do you want to start the process? (yes/start): ").lower().strip() in ["yes", "start"]:
            logging.info("Starting automation...")
            process_elements(driver, args.url, wait)
        else:
            logging.info("Process aborted by user.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
