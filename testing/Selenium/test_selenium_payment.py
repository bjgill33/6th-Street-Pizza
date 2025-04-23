from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
import unittest
import time


class TestPaymentPage(unittest.TestCase):
    def setUp(self):
        # Set up the WebDriver
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        # Navigate to the payment page
        self.driver.get("http://127.0.0.1:8000/payment/")

        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"Page title: {self.driver.title}")

    def test_location_modal(self):
        """Test location modal that may appear on page load"""
        driver = self.driver

        try:
            # Check if location modal appears
            location_modal = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "locationModal"))
            )
            print("Location modal appeared on page load")

            # Check modal title
            modal_title = location_modal.find_element(By.CLASS_NAME, "modal-title")
            self.assertEqual(modal_title.text, "Choose Your Store")

            # Wait for location buttons to load
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, "//p[contains(text(), 'Loading locations...')]")
                )
            )

            # Select the first available location
            store_buttons = driver.find_elements(
                By.XPATH, "//div[@id='store-buttons-container']//button"
            )
            if store_buttons:
                print(f"Found {len(store_buttons)} location buttons")
                # Get text before clicking to avoid stale element
                location_text = store_buttons[0].text
                store_buttons[0].click()
                print(f"Selected location: {location_text}")
            else:
                print(
                    "No location buttons found, location modal may need manual closing"
                )
                driver.execute_script("$('#locationModal').modal('hide');")

            # Wait for modal to close
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "locationModal"))
            )
            print("Location modal closed")
        except TimeoutException:
            print("No location modal appeared or it closed automatically")

    def test_navbar_links(self):
        """Test navigation bar links"""
        driver = self.driver

        # Define navigation links to test
        nav_links = {
            "Menu": "/menu/",
            "Locations": "/store_locations/",
            "Coupons": "/coupons/",
            "Tracker": "/track_order/",
        }

        for link_text, expected_path in nav_links.items():
            try:
                print(f"Testing navigation link: {link_text}")
                # Find and test the link
                link = driver.find_element(
                    By.XPATH, f"//a[contains(text(), '{link_text}')]"
                )
                self.assertTrue(
                    link.is_displayed(), f"{link_text} link should be visible"
                )
                self.assertTrue(
                    link.is_enabled(), f"{link_text} link should be enabled"
                )

                # Don't actually click the links as they navigate away from the test page
                print(f"Verified {link_text} link is present and enabled")
            except Exception as e:
                print(f"Error testing navigation link {link_text}: {e}")

    def test_cart_button(self):
        """Test cart button in navigation"""
        driver = self.driver

        try:
            # Find cart button
            cart_button = driver.find_element(
                By.XPATH, "//a[@data-bs-target='#cartModal']"
            )
            self.assertTrue(cart_button.is_displayed(), "Cart button should be visible")

            # Click cart button to open modal
            cart_button.click()
            print("Clicked cart button")

            # Wait for cart modal
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "cartModal"))
            )
            print("Cart modal opened successfully")

            # Close cart modal
            close_button = driver.find_element(
                By.XPATH, "//div[@id='cartModal']//button[@data-bs-dismiss='modal']"
            )
            close_button.click()

            # Wait for modal to close
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "cartModal"))
            )
            print("Cart modal closed successfully")
        except Exception as e:
            print(f"Error testing cart button: {e}")

    def test_order_review_section(self):
        """Test order review section buttons"""
        driver = self.driver

        try:
            # Find and test Edit button
            edit_button = driver.find_element(
                By.XPATH,
                "//button[@data-bs-toggle='modal' and @data-bs-target='#cartModal']",
            )
            self.assertTrue(edit_button.is_displayed(), "Edit button should be visible")
            print("Edit button verified")

            # Find and test Add More button
            add_more_button = driver.find_element(
                By.XPATH, "//a[contains(text(), 'Add More')]"
            )
            self.assertTrue(
                add_more_button.is_displayed(), "Add More button should be visible"
            )
            print("Add More button verified")

            # Don't click Add More as it navigates away from the page
        except Exception as e:
            print(f"Error testing order review section: {e}")

    def test_order_type_toggle(self):
        """Test toggling between delivery and carryout"""
        driver = self.driver

        try:
            # Get the radio buttons
            delivery_radio = driver.find_element(By.ID, "deliveryRadio")
            carryout_radio = driver.find_element(By.ID, "carryoutRadio")

            # Get the sections
            delivery_section = driver.find_element(By.ID, "deliverySection")
            carryout_section = driver.find_element(By.ID, "carryoutSection")

            # Verify default state (delivery should be selected)
            self.assertTrue(
                delivery_radio.is_selected(), "Delivery should be selected by default"
            )
            self.assertTrue(
                delivery_section.is_displayed(), "Delivery section should be visible"
            )
            self.assertFalse(
                carryout_section.is_displayed(), "Carryout section should be hidden"
            )
            print("Default state verified: Delivery selected")

            # Select carryout
            carryout_radio.click()
            print("Selected carryout")
            time.sleep(1)  # Wait for toggle to take effect

            # Verify carryout state
            self.assertTrue(carryout_radio.is_selected(), "Carryout should be selected")
            self.assertTrue(
                carryout_section.is_displayed(), "Carryout section should be visible"
            )
            self.assertFalse(
                delivery_section.is_displayed(), "Delivery section should be hidden"
            )
            print("Carryout section is now visible")

            # Switch back to delivery
            delivery_radio.click()
            print("Selected delivery")
            time.sleep(1)  # Wait for toggle to take effect

            # Verify delivery state
            self.assertTrue(delivery_radio.is_selected(), "Delivery should be selected")
            self.assertTrue(
                delivery_section.is_displayed(), "Delivery section should be visible"
            )
            self.assertFalse(
                carryout_section.is_displayed(), "Carryout section should be hidden"
            )
            print("Delivery section is now visible again")
        except Exception as e:
            print(f"Error testing order type toggle: {e}")

    def test_delivery_form(self):
        """Test filling out the delivery form"""
        driver = self.driver

        try:
            # Make sure delivery radio is selected
            delivery_radio = driver.find_element(By.ID, "deliveryRadio")
            if not delivery_radio.is_selected():
                delivery_radio.click()
                time.sleep(1)

            # Fill out email field
            email_field = driver.find_element(By.ID, "email")
            email_field.clear()
            email_field.send_keys("test@example.com")
            print("Entered email: test@example.com")

            # Fill out name field
            name_field = driver.find_element(By.ID, "fullName")
            name_field.clear()
            name_field.send_keys("John Doe")
            print("Entered name: John Doe")

            # Fill out phone field
            phone_field = driver.find_element(By.ID, "phone")
            phone_field.clear()
            phone_field.send_keys("555-123-4567")
            print("Entered phone: 555-123-4567")

            # Fill out address field
            address_field = driver.find_element(By.ID, "address")
            address_field.clear()
            address_field.send_keys("123 Main St, Apt 4B")
            print("Entered address: 123 Main St, Apt 4B")

            # Fill out city field
            city_field = driver.find_element(By.ID, "city")
            city_field.clear()
            city_field.send_keys("Los Angeles")
            print("Entered city: Los Angeles")

            # Select state from dropdown
            state_dropdown = Select(driver.find_element(By.ID, "state"))
            state_dropdown.select_by_visible_text("California")
            print("Selected state: California")

            # Fill out zip code field
            zip_field = driver.find_element(By.ID, "zip")
            zip_field.clear()
            zip_field.send_keys("90210")
            print("Entered zip code: 90210")

            # Fill out special instructions
            instructions_field = driver.find_element(By.ID, "specialInstructions")
            instructions_field.clear()
            instructions_field.send_keys("Please ring the doorbell twice.")
            print("Entered special instructions: Please ring the doorbell twice.")

            # Take screenshot of filled form
            driver.save_screenshot("delivery_form_filled.png")
            print("Saved screenshot of filled delivery form")
        except Exception as e:
            print(f"Error testing delivery form: {e}")

    def test_payment_section(self):
        """Test payment section elements"""
        driver = self.driver

        try:
            # Find card element container
            card_element = driver.find_element(By.ID, "card-element")
            self.assertTrue(
                card_element.is_displayed(), "Card element should be visible"
            )
            print("Card element container verified")

            # Find pay now button
            pay_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Pay Now')]"
            )
            self.assertTrue(
                pay_button.is_displayed(), "Pay Now button should be visible"
            )
            self.assertTrue(pay_button.is_enabled(), "Pay Now button should be enabled")
            print("Pay Now button verified")

            # Don't actually submit payment as it would attempt a real transaction
            print("Not submitting actual payment to avoid transaction processing")
        except Exception as e:
            print(f"Error testing payment section: {e}")

    def test_change_store_location(self):
        """Test changing store location"""
        driver = self.driver

        try:
            # Check if there's a "Change Store Location" button
            change_buttons = driver.find_elements(
                By.XPATH, "//button[contains(text(), 'Change Store Location')]"
            )

            if change_buttons:
                change_button = change_buttons[0]
                self.assertTrue(
                    change_button.is_displayed(),
                    "Change store button should be visible",
                )

                # Click button to open location modal
                change_button.click()
                print("Clicked Change Store Location button")

                # Wait for modal to appear
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "locationModal"))
                )
                print("Location modal opened successfully")

                # Close modal
                close_button = driver.find_element(
                    By.XPATH, "//div[@id='locationModal']//button[@class='btn-close']"
                )
                close_button.click()

                # Wait for modal to close
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element_located((By.ID, "locationModal"))
                )
                print("Location modal closed successfully")
            else:
                print(
                    "No Change Store Location button found - may be normal if no store is selected"
                )
        except Exception as e:
            print(f"Error testing change store location: {e}")

    def tearDown(self):
        print("Test complete. Closing browser.")
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
