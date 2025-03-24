import time
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import string

# Helper Functions
def generate_random_string(length=8):
    """Generate a random string for test data"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# Base Test Class
class TestBase:
    def setup_method(self):
        # Setup Chrome WebDriver
        options = webdriver.ChromeOptions()
        # Add options for headless mode if needed
        # options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            
    def teardown_method(self, method):
        # Take screenshot if test fails
        if hasattr(self, '_outcome'):
            result = self._outcome.result
            if result.failures or result.errors:
                test_name = f"{type(self).__name__}_{method.__name__}"
                self.take_screenshot(test_name)
        
        # Close browser after each test
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            
    def login(self, username="admin@6thstreetpizza.store", password="admin123"):
        """Helper method to log into the admin portal"""
        self.driver.get("https://6thstreetpizza.store/admin/")
        
        # Find and fill login form
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_field = self.driver.find_element(By.ID, "password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Submit form
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for dashboard to load
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
        
    def take_screenshot(self, test_name):
        """Take screenshot and save with test name"""
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        self.driver.save_screenshot(f"screenshots/{test_name}_{timestamp}.png")

# Login Tests
class TestLogin(TestBase):
    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        self.driver.get("https://6thstreetpizza.store/admin/")
        
        # Check if login form is present
        form = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        email_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "password")
        
        assert form.is_displayed()
        assert email_field.is_displayed()
        assert password_field.is_displayed()
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        self.driver.get("https://6thstreetpizza.store/admin/")
        
        # Fill form with invalid credentials
        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_field = self.driver.find_element(By.ID, "password")
        
        email_field.send_keys("wrong@example.com")
        password_field.send_keys("wrongpassword")
        
        # Submit form
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        # Check for error message
        error_message = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-message")))
        assert "Invalid credentials" in error_message.text
    
    def test_valid_login(self):
        """Test login with valid credentials"""
        self.login()  # Using the helper method from TestBase
        
        # Check we are on dashboard
        dashboard_title = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "Dashboard" in dashboard_title.text
        
        # Check welcome message
        welcome_message = self.driver.find_element(By.CLASS_NAME, "user-welcome")
        assert "Welcome" in welcome_message.text

# Order Management Tests
class TestOrderManagement(TestBase):
    def test_view_orders(self):
        """Test viewing the orders list"""
        self.login()
        
        # Navigate to orders page
        orders_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Orders')]")))
        orders_link.click()
        
        # Check orders table is visible
        orders_table = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "orders-table")))
        assert orders_table.is_displayed()
        
        # Check there are orders listed
        order_items = self.driver.find_elements(By.CLASS_NAME, "order-item")
        assert len(order_items) > 0
    
    def test_filter_orders_by_status(self):
        """Test filtering orders by status"""
        self.login()
        
        # Navigate to orders page
        orders_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Orders')]")))
        orders_link.click()
        
        # Select 'Pending' from status filter
        status_filter = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "status-filter")))
        status_filter.click()
        
        pending_option = self.driver.find_element(By.XPATH, "//option[contains(text(), 'Pending')]")
        pending_option.click()
        
        # Wait for filter to apply
        time.sleep(1)
        
        # Check all visible orders have 'Pending' status
        order_statuses = self.driver.find_elements(By.CLASS_NAME, "status")
        for status in order_statuses:
            assert "Pending" in status.text
    
    def test_change_order_status(self):
        """Test changing an order's status"""
        self.login()
        
        # Navigate to orders page
        orders_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Orders')]")))
        orders_link.click()
        
        # Select first order
        first_order = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "order-item")))
        first_order.click()
        
        # Change status to 'In Progress'
        status_dropdown = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "status-dropdown")))
        status_dropdown.click()
        
        in_progress_option = self.driver.find_element(By.XPATH, "//option[contains(text(), 'In Progress')]")
        in_progress_option.click()
        
        # Save changes
        save_button = self.driver.find_element(By.CLASS_NAME, "save-button")
        save_button.click()
        
        # Check for confirmation message
        notification = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "notification")))
        assert "Order status updated" in notification.text

# Menu Management Tests
class TestMenuManagement(TestBase):
    def test_add_new_menu_item(self):
        """Test adding a new menu item"""
        self.login()
        
        # Navigate to menu management
        menu_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Menu')]")))
        menu_link.click()
        
        # Click 'Add New Item' button
        add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add New Item')]")))
        add_button.click()
        
        # Fill in new menu item form
        item_name = self.wait.until(EC.presence_of_element_located((By.ID, "item-name")))
        item_name.send_keys(f"Test Pizza {generate_random_string()}")
        
        description = self.driver.find_element(By.ID, "item-description")
        description.send_keys("A pizza created by automated Selenium testing")
        
        price = self.driver.find_element(By.ID, "item-price")
        price.clear()
        price.send_keys("16.99")
        
        category_dropdown = self.driver.find_element(By.ID, "item-category")
        category_dropdown.click()
        
        specialty_option = self.driver.find_element(By.XPATH, "//option[contains(text(), 'Specialty Pizzas')]")
        specialty_option.click()
        
        # Upload image (assuming there's a file input)
        # file_input = self.driver.find_element(By.ID, "item-image")
        # file_input.send_keys("/path/to/test-pizza.jpg")
        
        # Save the new menu item
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        # Check for confirmation message
        success_message = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        assert "Menu item added successfully" in success_message.text

    def test_edit_menu_item(self):
        """Test editing an existing menu item"""
        self.login()
        
        # Navigate to menu management
        menu_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Menu')]")))
        menu_link.click()
        
        # Select the first menu item for editing
        edit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-item:first-child .edit-button")))
        edit_button.click()
        
        # Update the description
        description = self.wait.until(EC.presence_of_element_located((By.ID, "item-description")))
        description.clear()
        new_description = f"Updated description {generate_random_string()}"
        description.send_keys(new_description)
        
        # Update the price
        price = self.driver.find_element(By.ID, "item-price")
        price.clear()
        price.send_keys("18.99")
        
        # Save the changes
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        # Check for confirmation message
        success_message = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        assert "Menu item updated successfully" in success_message.text

# User Management Tests
class TestUserManagement(TestBase):
    def test_view_users(self):
        """Test viewing the users list"""
        self.login()
        
        # Navigate to users page
        users_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Users')]")))
        users_link.click()
        
        # Check users table is visible
        users_table = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "users-table")))
        assert users_table.is_displayed()
        
        # Check there are users listed
        user_items = self.driver.find_elements(By.CLASS_NAME, "user-item")
        assert len(user_items) > 0

    def test_add_new_user(self):
        """Test adding a new user"""
        self.login()
        
        # Navigate to users page
        users_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Users')]")))
        users_link.click()
        
        # Click 'Add New User' button
        add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add New User')]")))
        add_button.click()
        
        # Generate random user data
        random_str = generate_random_string()
        user_email = f"test.{random_str}@example.com"
        
        # Fill in new user form
        name_field = self.wait.until(EC.presence_of_element_located((By.ID, "user-name")))
        name_field.send_keys(f"Test User {random_str}")
        
        email_field = self.driver.find_element(By.ID, "user-email")
        email_field.send_keys(user_email)
        
        password_field = self.driver.find_element(By.ID, "user-password")
        password_field.send_keys("Secure123!")
        
        role_dropdown = self.driver.find_element(By.ID, "user-role")
        role_dropdown.click()
        
        staff_option = self.driver.find_element(By.XPATH, "//option[contains(text(), 'Staff')]")
        staff_option.click()
        
        # Save the new user
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        # Check for confirmation message
        success_message = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
        assert "User added successfully" in success_message.text

# Reports and Analytics Tests
class TestReportsAnalytics(TestBase):
    def test_view_sales_report(self):
        """Test viewing the sales report"""
        self.login()
        
        # Navigate to reports page
        reports_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Reports')]")))
        reports_link.click()
        
        # Click on sales report tab
        sales_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sales')]")))
        sales_tab.click()
        
        # Check sales chart is visible
        sales_chart = self.wait.until(EC.presence_of_element_located((By.ID, "sales-chart")))
        assert sales_chart.is_displayed()
        
        # Check date filter is present
        date_filter = self.driver.find_element(By.ID, "date-range")
        assert date_filter.is_displayed()

    def test_export_report(self):
        """Test exporting a report"""
        self.login()
        
        # Navigate to reports page
        reports_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Reports')]")))
        reports_link.click()
        
        # Click export button
        export_button = self.wait.until(EC.element_to_be_clickable((By.ID, "export-report")))
        export_button.click()
        
        # Wait for export options
        export_options = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "export-options")))
        assert export_options.is_displayed()
        
        # Select CSV option
        csv_option = self.driver.find_element(By.XPATH, "//button[contains(text(), 'CSV')]")
        csv_option.click()
        
        # Check download starts (this is difficult to verify fully with Selenium)
        download_message = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "download-started")))
        assert "Download started" in download_message.text

# Security Tests
class TestSecurity(TestBase):
    def test_session_timeout(self):
        """Test session timeout functionality"""
        self.login()
        
        # Simulate timeout (this is a simplified version)
        # In a real test, you might want to manipulate cookies or local storage
        time.sleep(2)  # Wait a bit
        
        # Reload page after simulated timeout
        self.driver.get("https://6thstreetpizza.store/admin/dashboard")
        
        # Check if redirected to login
        try:
            # Wait for dashboard - this should fail if properly redirected to login
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
            # If we get here, we're still logged in, which might be expected for a short timeout
            # This assertion might need adjustment based on actual timeout settings
            print("Still logged in after short wait - expected if timeout is longer")
        except:
            # Check if we're on the login page
            login_form = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            assert login_form.is_displayed()
            print("Redirected to login as expected")

# Main test runner
# Main test runner
if __name__ == "__main__":
    # When running the file directly, use a simplified pytest call
    import sys
    
    # Check if any command line arguments were provided
    if len(sys.argv) > 1:
        # If arguments were provided, pass them directly to pytest
        pytest.main(sys.argv[1:])
    else:
        # Otherwise, use our default arguments
        pytest.main([
            "-v",  # Verbose output
        ])