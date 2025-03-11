from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Initialize WebDriver (Change the path to your driver if needed)
driver = webdriver.Chrome()

# Step 1: Open the index.html page
driver.get("http://localhost:8000/index.html")  # Replace with the actual file path

# Step 2: Click on the "Menu" link
menu_link = driver.find_element(By.LINK_TEXT, "Menu")
menu_link.click()

# Step 3: Wait and verify if menu page loads
time.sleep(2)  # Allow time for the page to load
assert "Menu" in driver.title

# Step 4: Verify presence of a pizza menu item
try:
    pizza_item = driver.find_element(By.ID, "pepperoni_pizza")  # Verify ID exists
    print("Pepperoni Pizza found on menu page.")
except:
    print("Pepperoni Pizza not found!")

# Step 5: Click on "Order Now" for a pizza item
order_button = pizza_item.find_element(By.TAG_NAME, "a")  # Find button inside card
order_button.click()
time.sleep(2)  # Allow time for response

# Step 6: Check if the cart modal is displayed (if applicable)
try:
    cart_modal = driver.find_element(By.ID, "cartModal")
    assert cart_modal.is_displayed()
    print("Cart Modal is displayed successfully.")
except:
    print("Cart Modal is NOT displayed!")

# Close the browser
driver.quit()
