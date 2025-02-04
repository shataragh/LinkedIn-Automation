from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize Chrome WebDriver with options to suppress logs
options = webdriver.ChromeOptions()
options.add_argument("--disable-webrtc")  # Disable WebRTC to suppress STUN errors
options.add_argument("--log-level=3")    # Suppress non-fatal logs
driver = webdriver.Chrome(options=options)

# Open the LinkedIn page
target_url = "https://www.linkedin.com/mynetwork/catch-up/all/"
driver.get(target_url)

# Wait for the page to load completely
wait = WebDriverWait(driver, 10)

def get_scroll_position():
    """Get the current vertical scroll position of the page."""
    return driver.execute_script("return window.scrollY;")

def scroll_down():
    """Scroll down the page to load more content."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for new content to load

def is_on_target_page():
    """Check if the current URL matches the target page."""
    current_url = driver.current_url
    return current_url.startswith(target_url)

def find_congrats_on_elements():
    """Find all elements containing the text 'Congrats on'."""
    return driver.find_elements(By.XPATH, "//span[contains(text(), 'Congrats on')] | //div[contains(., 'Congrats on')]")

def click_and_send(element):
    """Click an element associated with 'Congrats on' and send the message."""
    try:
        # Check if still on the target page
        if not is_on_target_page():
            print("Navigated away from the target page. Stopping the process.")
            return
        
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Short delay to mimic human behavior
        
        # Check if the element is interactable
        if not element.is_displayed() or not element.is_enabled():
            print(f"Element is not interactable: {element.tag_name}")
            return
        
        # Find the clickable button or link within the parent element
        clickable_element = None
        try:
            clickable_element = element.find_element(By.XPATH, ".//button | .//a")
        except Exception:
            print("No clickable child element found within the parent element.")
            return
        
        # Verify that clicking won't navigate away
        if clickable_element.tag_name == "a":
            print("Skipping element because it's a link that may navigate away.")
            return
        
        # Click the clickable element
        clickable_element.click()
        
        # Check if still on the target page after clicking
        if not is_on_target_page():
            print("Navigated away from the target page. Stopping the process.")
            return
        
        # Wait for the prompt to appear and click "Send"
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]")))
        time.sleep(0.5)  # Short delay to mimic human behavior
        send_button.click()
        
        # Check for success messages
        message_sent = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Message sent')]")))
        message_success = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Message sent successfully')]")))
        
        if message_sent and message_success:
            print("Message sent successfully!")
        else:
            print("Failed to send message.")
    
    except Exception as e:
        print(f"Error processing an element: {e}")

def process_all_congrats_on():
    """Process all elements containing 'Congrats on' on the page."""
    last_scroll_position = 0
    
    while True:
        # Check if still on the target page
        if not is_on_target_page():
            print("Navigated away from the target page. Stopping the process.")
            break
        
        # Monitor the current scroll position
        current_scroll_position = get_scroll_position()
        
        # Check if the user has scrolled down manually
        if current_scroll_position > last_scroll_position:
            print("Detected user scroll. Searching for new 'Congrats on' elements...")
            last_scroll_position = current_scroll_position
        
        # Find all visible elements containing 'Congrats on'
        congrats_on_elements = find_congrats_on_elements()
        
        if not congrats_on_elements:
            print("No 'Congrats on' elements found. Scrolling down automatically...")
            scroll_down()
            continue
        
        # Process each element one by one
        for i, element in enumerate(congrats_on_elements):
            print(f"Processing 'Congrats on' element {i + 1} of {len(congrats_on_elements)}...")
            click_and_send(element)
            time.sleep(1)  # Maximum delay of 1 second between clicks
        
        # After processing all elements, scroll down to check for more
        print("Finished processing current batch. Scrolling down to check for more...")
        scroll_down()

def main():
    """Main function to ask for user confirmation before starting the automation."""
    user_input = input("Do you want to start the process? (Yes, Start): ").strip().lower()
    
    if user_input == "yes, start":
        print("Starting the process...")
        process_all_congrats_on()
    else:
        print("Process aborted by the user.")

# Start the program
try:
    main()
finally:
    # Close the browser after completion
    driver.quit()