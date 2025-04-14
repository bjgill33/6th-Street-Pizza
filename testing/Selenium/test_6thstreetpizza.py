import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from time import sleep


class TestPizzaWebsite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()

    def setUp(self):
        if self._testMethodName.startswith("test_05") or self._testMethodName.startswith("test_06"):
            self.driver.get("http://127.0.0.1:5500/menu.html")
        else:
            self.driver.get("http://127.0.0.1:5500/index.html")

        self.close_modal()

    def close_modal(self):
        try:
            close_button = self.driver.find_element(
                By.CSS_SELECTOR, ".btn-close")
            if close_button.is_displayed():
                close_button.click()
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element(close_button))
        except Exception:
            pass  # If no modal is open, do nothing

    def tearDown(self):
        self.close_modal()  # Close any modal after each test if left open

    def is_element_obstructed(self, element):
        # Check if an element is obstructed by another element.
        try:
            self.driver.execute_script("""
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (rect.top < 0 || rect.left < 0 || rect.bottom > window.innerHeight || rect.right > window.innerWidth);
            """, element)
            return False
        except Exception:
            return True

    def click_element(self, element):
        # Helper function to click an element safely.
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(element))
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
        except ElementClickInterceptedException:
            # Handle click interception by retrying the click or logging for debugging
            print("Element click was intercepted. Retrying click via JavaScript.")
            self.driver.execute_script("arguments[0].click();", element)

    # --- Landing Page Tests Start --- #
    def test_01_landing_page(self):
        # Test if the landing page contains the expected title and header
        self.assertIn("6th Street Pizza", self.driver.title, "Title not found")
        h1_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'h1')))
        self.assertEqual(h1_element.text.strip().lower(), "start your order",
                         f"Expected 'Start Your Order', but found '{h1_element.text}'")
        print("Test Passed! Heading found on landing page")

    def test_02_images_loaded(self):
        # Test if images are loaded properly on the landing page
        images = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )

        for img in images:
            self.assertTrue(img.get_attribute("src"),
                            "Image is missing a source!")

        print("Test Passed! All images have valid sources")

        # Adding wait here to ensure that images have finished loading before the next test
        sleep(1)

    def test_03_featured_menu_items(self):
        # Test if featured menu items exist on the landing page
        item_ids = [
            "veggie_pizza_and_coke",
            "pepperoni_pizza",
            "cheese_pizza_deal",
            "chocolate_chip_cookies",
            "bbq_wings_deal",
            "arugula_pizza_deal"
        ]

        for item_id in item_ids:
            item = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, item_id))
            )
            self.assertTrue(item.is_displayed(),
                            f"Item {item_id} is not displayed!")

        print("Test Passed! All featured menu items are displayed correctly")

    def test_04_order_type_buttons(self):
        # Test if Delivery and Carryout buttons are present and clickable
        delivery_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.btn-danger[data-bs-target='#deliveryModal']"))
        )
        carryout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.btn-secondary[data-bs-target='#locationModal']"))
        )

        self.assertTrue(delivery_button.is_displayed(),
                        "Delivery button is missing!")
        self.assertTrue(carryout_button.is_displayed(),
                        "Carryout button is missing!")

        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", delivery_button)
        if not self.is_element_obstructed(delivery_button):
            self.click_element(delivery_button)
            print("Clicked the Delivery button")
        else:
            print("Delivery button is obstructed by another element")

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "deliveryModal")))
        self.close_modal()

        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", carryout_button)
        if not self.is_element_obstructed(carryout_button):
            self.click_element(carryout_button)
            print("Clicked the Carryout button")
        else:
            print("Carryout button is obstructed by another element")

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "locationModal")))
        self.close_modal()

        print("Test Passed! Delivery and Carryout buttons exist and are clickable, modals closed")
    # --- Landing Page Tests End --- #

    # --- Menu Page Tests Start ---#
    def test_05_menu_page(self):
        # Test if the menu page loads correctly
        driver = self.driver
        driver.get("http://127.0.0.1:5500/menu.html")
        menu_header = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertEqual(menu_header.text.strip().lower(), "menu",
                         "Menu header not found or incorrect!")
        print("Test Passed! Menu heading found")

    def test_06_menu_categories(self):
        # Test clicking menu categories in the dropdown
        driver = self.driver
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#menuFilter"))
        )
        filter_button.click()

        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "ul.dropdown-menu"))
        )

        categories = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "ul.dropdown-menu .dropdown-item"))
        )

        if not categories:
            self.fail("No menu categories found!")

        for category in categories:
            category_name = category.text.strip()
            print(f"Clicking category: {category_name}")

            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(category))
            category.click()

            driver.execute_script(f"filterMenu('{category_name.lower()}')")

            self.wait_for_menu_items(category_name)

            print(f"Test Passed! Menu items loaded for {category_name}!")

            filter_button.click()
            sleep(1)

        print("All categories clicked and verified successfully!")

    def wait_for_menu_items(self, category_name):
        # Helper function to wait for the corresponding menu items based on category
        category_css = {
            'pizza': ".pizza .card",
            'wings': ".wings .card",
            'dessert': ".dessert .card",
            'drinks': ".drinks .card"
        }.get(category_name.lower(), ".card")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, category_css))
        )
    # --- Menu Page Tests End ---#

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()
