import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class TestPizzaWebsite:
    @pytest.fixture(scope="function")
    def driver(self):
        # Setup Chrome driver with options
        options = webdriver.ChromeOptions()
        
        # Uncomment the line below to run headless (without browser UI)
        # options.add_argument("--headless=new")
        
        # Create driver with managed ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Set a default window size
        driver.set_window_size(1366, 768)
        
        # Implicit wait for elements to be found
        driver.implicitly_wait(10)
        
        # Pass driver to test
        yield driver
        
        # Quit driver after test
        driver.quit()
        
    # Base URL for the application - adjust according to your setup
    BASE_URL = "http://localhost:8000"  # Change to match your development server
    
    def test_homepage_loads(self, driver):
        """Test that the homepage loads successfully."""
        driver.get(f"{self.BASE_URL}/index.html")
        
        # Check for the logo
        logo = driver.find_element(By.CSS_SELECTOR, ".navbar-brand img")
        assert logo.is_displayed(), "Logo should be visible"
        
        # Check for the start your order section
        order_section = driver.find_element(By.CLASS_NAME, "order-section")
        assert order_section.is_displayed(), "Order section should be visible"
        
        # Check for delivery and carryout buttons
        delivery_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#deliveryModal']")
        assert delivery_btn.is_displayed(), "Delivery button should be visible"
        assert "Delivery" in delivery_btn.text, "Button should say 'Delivery'"
        
        carryout_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#locationModal']")
        assert carryout_btn.is_displayed(), "Carryout button should be visible"
        assert "Carryout" in carryout_btn.text, "Button should say 'Carryout'"
    
    def test_menu_page_loads(self, driver):
        """Test that the menu page loads successfully."""
        driver.get(f"{self.BASE_URL}/menu.html")
        
        # Check for the menu heading
        menu_heading = driver.find_element(By.TAG_NAME, "h1")
        assert menu_heading.text == "Menu", "Menu heading should be 'Menu'"
        
        # Check that menu filter is present
        filter_btn = driver.find_element(By.ID, "menuFilter")
        assert filter_btn.is_displayed(), "Menu filter button should be visible"
        
        # Check that menu items are displayed
        menu_items = driver.find_elements(By.ID, "menuItems")
        assert len(menu_items) > 0, "Menu items should be present"
        
        # Check for different menu categories
        pizza_items = driver.find_elements(By.CLASS_NAME, "pizza")
        assert len(pizza_items) > 0, "Pizza items should be present"
        
        wings_items = driver.find_elements(By.CLASS_NAME, "wings")
        assert len(wings_items) > 0, "Wings items should be present"
    
    def test_menu_filter(self, driver):
        """Test that the menu filter functionality works."""
        driver.get(f"{self.BASE_URL}/menu.html")
        
        # Click on filter dropdown
        filter_btn = driver.find_element(By.ID, "menuFilter")
        filter_btn.click()
        
        # Wait for dropdown to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".dropdown-menu"))
        )
        
        # Click on the pizza filter
        pizza_filter = driver.find_element(By.CSS_SELECTOR, ".dropdown-item[onclick=\"filterMenu('pizza')\"]")
        pizza_filter.click()
        
        # Wait for filter to apply
        time.sleep(1)
        
        # Check that only pizza items are visible
        visible_items = driver.find_elements(By.CSS_SELECTOR, ".col-md-4.mb-4:not([style*='display: none'])")
        pizza_items = driver.find_elements(By.CLASS_NAME, "pizza")
        assert len(visible_items) == len(pizza_items), "Only pizza items should be visible after filtering"
    
    def test_delivery_modal(self, driver):
        """Test the delivery modal form."""
        driver.get(f"{self.BASE_URL}/index.html")
        
        # Click delivery button
        delivery_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#deliveryModal']")
        delivery_btn.click()
        
        # Wait for modal to appear
        modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "deliveryModal"))
        )
        
        # Fill out the form
        driver.find_element(By.ID, "fullName").send_keys("John Smith")
        driver.find_element(By.ID, "email").send_keys("john.smith@example.com")
        driver.find_element(By.ID, "address").send_keys("123 Main St")
        driver.find_element(By.ID, "city").send_keys("Anytown")
        driver.find_element(By.ID, "state").send_keys("CA")
        driver.find_element(By.ID, "zip").send_keys("12345")
        driver.find_element(By.ID, "phone").send_keys("(555) 123-4567")
        driver.find_element(By.ID, "specialInstructions").send_keys("Please knock loudly")
        
        # Submit form (we're not actually submitting to avoid side effects)
        # Just check that all fields are filled correctly
        assert driver.find_element(By.ID, "fullName").get_attribute("value") == "John Smith"
        assert driver.find_element(By.ID, "email").get_attribute("value") == "john.smith@example.com"
    
    def test_add_to_cart(self, driver):
        """Test adding an item to the cart."""
        driver.get(f"{self.BASE_URL}/menu.html")
        
        # Find the first order button and click it
        order_btns = driver.find_elements(By.CSS_SELECTOR, ".btn-primary.btn-sm")
        first_item_btn = order_btns[0]
        
        # Get the item name
        item_card = first_item_btn.find_element(By.XPATH, "./ancestor::div[contains(@class, 'card')]")
        item_title = item_card.find_element(By.CSS_SELECTOR, ".card-title").text
        
        # Click to add to cart
        first_item_btn.click()
        
        # Check that cart badge updates
        cart_badge = WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "cartBadge"), "1")
        )
        assert cart_badge, "Cart badge should update to 1"
        
        # Open cart modal
        cart_icon = driver.find_element(By.CSS_SELECTOR, ".bi-cart")
        cart_icon.click()
        
        # Wait for cart modal to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "cartModal"))
        )
        
        # Check item is in cart (this will need to be adapted to your actual cart implementation)
        # This is a placeholder assertion that assumes the cart shows items
        cart_items = driver.find_elements(By.CSS_SELECTOR, "#cartModal .cart-item")
        assert len(cart_items) > 0, "Cart should contain at least one item"

    def test_navigation_between_pages(self, driver):
        """Test navigation between homepage and menu page."""
        # Start on homepage
        driver.get(f"{self.BASE_URL}/index.html")
        
        # Click menu link
        menu_link = driver.find_element(By.CSS_SELECTOR, "a[href='menu.html']")
        menu_link.click()
        
        # Verify we're on menu page
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Menu")
        )
        assert "menu.html" in driver.current_url, "URL should contain menu.html"
        
        # Navigate back to homepage
        logo_link = driver.find_element(By.CSS_SELECTOR, ".navbar-brand")
        logo_link.click()
        
        # Verify we're back on the homepage
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "order-section"))
        )
        assert "index.html" in driver.current_url, "URL should contain index.html"
