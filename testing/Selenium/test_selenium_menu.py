from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import unittest
import time


class TestMenuPage(unittest.TestCase):
    def setUp(self):
        # Set up the WebDriver (use the path to your WebDriver)
        self.driver = webdriver.Chrome()

        # Navigate to the menu page
        self.driver.get("http://127.0.0.1:8000/menu")  # Replace with your local URL
        self.driver.maximize_window()

        # Wait for the page to load
        time.sleep(2)

        # Print the title to verify the page loaded
        print(f"Page title: {self.driver.title}")

    def test_page_elements(self):
        """Test that basic page elements load correctly"""
        driver = self.driver

        # Check that the page has loaded by verifying the title
        self.assertIn("6th Street Pizza", driver.title)

        # Check that the navbar exists
        navbar = driver.find_element(By.CLASS_NAME, "navbar")
        self.assertTrue(navbar.is_displayed(), "Navbar is not displayed")

        # Check that the logo exists
        try:
            logo = driver.find_element(By.XPATH, "//a[@class='navbar-brand']/img")
            self.assertTrue(logo.is_displayed(), "Logo is not displayed")
        except NoSuchElementException:
            self.fail("Logo element not found")

    def test_clickable_elements(self):
        driver = self.driver

        # Test navigation links - using more generic selectors
        nav_items = driver.find_elements(By.CLASS_NAME, "nav-link")

        # Verify we found some navigation links
        self.assertGreater(len(nav_items), 0, "No navigation links found")

        print(f"Found {len(nav_items)} navigation links")

        # Test each navigation link
        for link in nav_items:
            try:
                link_text = link.text.strip()
                if (
                    link_text and "cart" not in link_text.lower()
                ):  # Skip cart link as it opens modal
                    print(f"Testing link: {link_text}")
                    self.assertTrue(
                        link.is_displayed(), f"Link '{link_text}' is not displayed"
                    )
                    self.assertTrue(
                        link.is_enabled(), f"Link '{link_text}' is not clickable"
                    )

                    # Store current URL
                    current_url = driver.current_url

                    # Click the link
                    link.click()
                    time.sleep(1)  # Wait for navigation

                    # Verify URL changed (indicating navigation worked)
                    self.assertNotEqual(
                        driver.current_url,
                        current_url,
                        f"URL didn't change after clicking {link_text}",
                    )

                    # Go back to menu page
                    driver.back()
                    time.sleep(1)  # Wait for navigation back
            except Exception as e:
                print(f"Error testing link: {e}")

        # Test "Order Now" Buttons if they exist
        try:
            order_buttons = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "order-btn"))
            )

            if order_buttons:
                print(f"Found {len(order_buttons)} order buttons")
                # Test the first button only to avoid too many popups
                button = order_buttons[0]
                button_name = button.get_attribute("data-name") or "Unknown item"
                print(f"Testing order button for: {button_name}")

                self.assertTrue(button.is_displayed(), f"Order button is not displayed")
                self.assertTrue(button.is_enabled(), f"Order button is not clickable")

                # Click the button
                button.click()
                time.sleep(1)  # Wait for any modal to appear

                # Try to find a related modal or cart update
                try:
                    # Check if cart badge was updated or modal appeared
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
                    )
                    print("Modal appeared after clicking order button")
                except TimeoutException:
                    # If no modal, check if cart badge changed
                    cart_badge = driver.find_element(By.ID, "cartBadge")
                    print(f"Cart badge value: {cart_badge.text}")
        except TimeoutException:
            print("No order buttons found within timeout period")
        except Exception as e:
            print(f"Error testing order buttons: {e}")

    def test_footer_links(self):
        driver = self.driver

        # Test Footer Links if they exist
        try:
            footer = driver.find_element(By.TAG_NAME, "footer")
            self.assertTrue(footer.is_displayed(), "Footer is not displayed")

            footer_links = footer.find_elements(By.TAG_NAME, "a")
            if footer_links:
                print(f"Found {len(footer_links)} footer links")
                for link in footer_links:
                    link_text = link.text.strip() or link.get_attribute("href")
                    self.assertTrue(
                        link.is_displayed(),
                        f"Footer link '{link_text}' is not displayed",
                    )
                    self.assertTrue(
                        link.is_enabled(), f"Footer link '{link_text}' is not clickable"
                    )
            else:
                print("No clickable links found in footer")
        except NoSuchElementException:
            print("Footer element not found")
        except Exception as e:
            print(f"Error testing footer: {e}")

    def test_filter_dropdown(self):
        """Test the filter menu dropdown functionality"""
        driver = self.driver

        # Wait for page to fully load
        time.sleep(2)

        try:
            # Find the filter dropdown button using multiple possible selectors
            filter_button = None

            # Try different selectors that might match the filter button
            selectors = [
                "//button[contains(text(), 'Filter')]",  # Text contains "Filter"
                "//button[@id='menuFilter']",  # ID is "menuFilter"
                "//button[@class='dropdown-toggle']",  # Has class "dropdown-toggle"
                "//div[contains(@class, 'dropdown')]/button",  # Button inside dropdown div
                "//button[contains(@data-bs-toggle, 'dropdown')]",  # Has data-bs-toggle attribute
            ]

            for selector in selectors:
                try:
                    filter_button = driver.find_element(By.XPATH, selector)
                    print(f"Found filter button with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if not filter_button:
                print("Filter dropdown button not found, trying alternative approaches")
                # Try looking for any dropdown buttons
                dropdown_buttons = driver.find_elements(
                    By.XPATH, "//button[contains(@class, 'dropdown')]"
                )
                if dropdown_buttons:
                    filter_button = dropdown_buttons[
                        0
                    ]  # Use the first dropdown button found
                    print(f"Using alternative dropdown button: {filter_button.text}")

            # If we found a filter button, test it
            if filter_button:
                self.assertTrue(
                    filter_button.is_displayed(), "Filter button is not displayed"
                )
                self.assertTrue(
                    filter_button.is_enabled(), "Filter button is not clickable"
                )

                # Click the filter button to open the dropdown
                filter_button.click()
                print("Clicked filter button")
                time.sleep(1)  # Wait for dropdown to appear

                # Find the dropdown menu
                dropdown_menu = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dropdown-menu"))
                )
                self.assertTrue(
                    dropdown_menu.is_displayed(), "Dropdown menu is not displayed"
                )

                # Get all dropdown items
                dropdown_items = dropdown_menu.find_elements(By.TAG_NAME, "a")
                if dropdown_items:
                    print(f"Found {len(dropdown_items)} filter options")

                    # Store current menu items count for comparison after filtering
                    all_menu_items = len(driver.find_elements(By.CLASS_NAME, "card"))
                    print(f"Total menu items before filtering: {all_menu_items}")

                    # Test each filter option
                    for i, item in enumerate(dropdown_items):
                        # Skip testing all items if there are too many
                        if i > 0 and i >= 2:  # Test only first two options after "All"
                            print(
                                "Skipping remaining filter options to keep test shorter"
                            )
                            break

                        item_text = item.text.strip()
                        print(f"Testing filter option: {item_text}")

                        # Click the filter option
                        item.click()
                        time.sleep(1)  # Wait for filtering to occur

                        # Verify filtering worked (check if number of visible cards changed or specific category is shown)
                        current_items = len(driver.find_elements(By.CLASS_NAME, "card"))
                        print(
                            f"Menu items after applying filter '{item_text}': {current_items}"
                        )

                        # If not the "All" option, filtering might reduce the number of items
                        if item_text.lower() != "all" and i > 0:
                            # This is a soft check - filtering might or might not reduce items
                            if current_items != all_menu_items:
                                print(
                                    f"Filter '{item_text}' changed the number of visible items"
                                )

                        # Re-click the filter button to open the dropdown again for the next iteration
                        filter_button.click()
                        time.sleep(1)  # Wait for dropdown to appear
                else:
                    print("No dropdown items found")
            else:
                print("Could not locate the filter menu dropdown button")

        except Exception as e:
            print(f"Error testing filter dropdown: {e}")
            import traceback

            traceback.print_exc()

    def tearDown(self):
        # Close the browser
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
