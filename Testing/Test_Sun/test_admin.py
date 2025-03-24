from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Step 1: Launch the browser
driver = webdriver.Chrome()
driver.maximize_window()

# Step 2: Navigate to the admin login page
driver.get("https://6thstreetpizza.store/admin/")

# Optional: Wait for the page to load
time.sleep(2)

# Step 3: Locate and fill in the login form
username_input = driver.find_element(By.NAME, "Email:")
password_input = driver.find_element(By.NAME, "Password:")

username_input.send_keys("group6pizza@yahoo.com")  # Replace with valid username
password_input.send_keys("ldgctiwenEfzerg8y9834982#2A")  # Replace with valid password
password_input.send_keys(Keys.RETURN)      # Press Enter to submit

# Step 4: Wait and check if login is successful
time.sleep(3)

# Step 5: Check the resulting URL or page content
if "/admin/dashboard" in driver.current_url or "Logout" in driver.page_source:
    print("✅ Login successful.")
else:
    print("❌ Login failed.")

# Step 6: Close the browser
driver.quit()
