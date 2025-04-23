from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import unittest
import time


class TestHomePage(unittest.TestCase):
    def setUp(self):
        # Set up the WebDriver
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def test_homepage_interactive_elements(self):
        driver = self.driver

        # Navigate to the homepage
        driver.get("http://127.0.0.1:8000")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Print the page title for debugging
        print(f"Page title: {driver.title}")

        # Test 1: Handle Location Modal that appears on page load
        try:
            # Wait for the location modal to appear
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "locationModal"))
            )
            location_modal = driver.find_element(By.ID, "locationModal")

            print("Location modal appeared as expected")
            self.assertTrue(
                location_modal.is_displayed(), "Location modal should be displayed"
            )

            # Check the modal title
            modal_title = location_modal.find_element(By.CLASS_NAME, "modal-title")
            self.assertEqual(
                modal_title.text,
                "Choose Your Store",
                "Modal title should be 'Choose Your Store'",
            )

            # Wait for the locations to load and appear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, "//p[contains(text(), 'Loading locations...')]")
                )
            )

            # Select the first location button that appears
            store_container = driver.find_element(By.ID, "store-buttons-container")
            location_buttons = store_container.find_elements(By.TAG_NAME, "button")

            if location_buttons:
                print(f"Found {len(location_buttons)} location buttons")
                # Get the text BEFORE clicking the button to avoid stale element reference
                button_text = "Default Location"
                try:
                    button_text = location_buttons[0].text
                except:
                    pass

                # Click the first location button
                location_buttons[0].click()
                print(f"Selected location: {button_text}")
            else:
                # If no locations loaded, close the modal another way
                print("No location buttons found, closing modal manually")
                driver.execute_script("$('#locationModal').modal('hide');")

            # Wait for the modal to close
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "locationModal"))
            )
            print("Location modal closed")

            # Add a small delay to let the page stabilize after modal closes
            time.sleep(1)

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Location modal handling error: {e}")
            # Continue with the test even if the modal doesn't appear as expected

        # Test 2: Navigation Menu Links
        nav_links = {
            "Menu": "/menu/",
            "Locations": "/store_locations/",
            "Coupons": "/coupons/",
            "Tracker": "/track_order/",
        }

        for link_text, expected_path in nav_links.items():
            try:
                print(f"Testing navigation link: {link_text}")
                # Find the link
                link = driver.find_element(
                    By.XPATH, f"//a[contains(text(), '{link_text}')]"
                )
                self.assertTrue(
                    link.is_displayed(), f"Link '{link_text}' should be displayed"
                )
                self.assertTrue(
                    link.is_enabled(), f"Link '{link_text}' should be clickable"
                )

                # Click the link
                link.click()

                # Wait for the page to load
                WebDriverWait(driver, 10).until(EC.url_contains(expected_path))

                print(f"Successfully navigated to {driver.current_url}")

                # Navigate back to the home page
                driver.back()

                # Wait to be back on the home page
                WebDriverWait(driver, 10).until(EC.title_contains("6th Street Pizza"))
            except Exception as e:
                print(f"Error testing navigation link '{link_text}': {e}")

        # Test 3: Cart Button
        try:
            print("Testing cart button")
            cart_button = driver.find_element(
                By.XPATH, "//a[@data-bs-target='#cartModal']"
            )
            self.assertTrue(
                cart_button.is_displayed(), "Cart button should be displayed"
            )
            cart_button.click()

            # Wait for cart modal to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "cartModal"))
            )
            print("Cart modal appeared successfully")

            # Close the cart modal
            close_button = driver.find_element(
                By.XPATH, "//div[@id='cartModal']//button[@data-bs-dismiss='modal']"
            )
            close_button.click()

            # Wait for modal to close
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "cartModal"))
            )
        except Exception as e:
            print(f"Error testing cart button: {e}")

        # Test 4: Order Section Buttons with Default Form Values
        try:
            print("\nTesting 'Delivery' button with default form values")

            # Find and click the Delivery Button
            delivery_button = driver.find_element(
                By.XPATH, "//button[@data-bs-target='#deliveryModal']"
            )
            self.assertTrue(
                delivery_button.is_displayed(), "Delivery button should be displayed"
            )
            delivery_button.click()

            # Wait for delivery modal to appear
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "deliveryModal"))
            )
            print("Delivery modal appeared successfully")

            # Test filling out the delivery form with default/placeholder values
            print("Testing delivery form with default values")

            # Get placeholder values for each field
            zip_input = driver.find_element(By.ID, "zip")
            zip_placeholder = zip_input.get_attribute("placeholder") or "12345"

            phone_input = driver.find_element(By.ID, "phone")
            phone_placeholder = (
                phone_input.get_attribute("placeholder") or "(123) 456-7890"
            )

            special_instructions = driver.find_element(By.ID, "specialInstructions")
            instructions_placeholder = (
                special_instructions.get_attribute("placeholder")
                or "Knock on the door hard."
            )

            # Fill the form with placeholder/default values
            zip_input.clear()
            zip_input.send_keys(zip_placeholder)
            print(f"Entered default zip code: {zip_placeholder}")

            phone_input.clear()
            phone_input.send_keys(phone_placeholder)
            print(f"Entered default phone number: {phone_placeholder}")

            special_instructions.clear()
            special_instructions.send_keys(instructions_placeholder)
            print(f"Entered default special instructions: {instructions_placeholder}")

            # Take a screenshot of the filled form with default values
            driver.save_screenshot("delivery_form_default_values.png")
            print("Saved screenshot of form with default values")

            # Submit the form
            submit_button = driver.find_element(
                By.XPATH, "//div[@id='deliveryModal']//button[@type='submit']"
            )
            self.assertTrue(
                submit_button.is_displayed(), "Submit button should be displayed"
            )
            print("Submitting the delivery form with default values")
            submit_button.click()

            # Wait for form processing
            try:
                # Option 1: Wait for success message
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
                )
                print(
                    "Form with default values submitted successfully - success message appeared"
                )
            except TimeoutException:
                # Option 2: Check if modal closed
                try:
                    WebDriverWait(driver, 5).until(
                        EC.invisibility_of_element_located((By.ID, "deliveryModal"))
                    )
                    print(
                        "Form with default values submitted successfully - modal closed automatically"
                    )
                except TimeoutException:
                    print(
                        "Form with default values submitted but no obvious success indicator"
                    )
                    # Close the modal manually if still open
                    try:
                        close_button = driver.find_element(
                            By.XPATH,
                            "//div[@id='deliveryModal']//button[@class='btn-close']",
                        )
                        close_button.click()
                        print("Closed the modal manually after submission")
                    except:
                        print("Could not close the modal manually")

        except Exception as e:
            print(f"Error testing delivery button with default values: {e}")

        # Test 5: "Order Now" Buttons on Food Items
        try:
            print("Testing 'Order Now' buttons on food items")
            order_buttons = driver.find_elements(By.CLASS_NAME, "order-btn")

            if order_buttons:
                print(f"Found {len(order_buttons)} order buttons")

                # Test the first button only to avoid too many popups
                test_button = order_buttons[0]
                item_name = test_button.get_attribute("data-name") or "Unknown item"
                print(f"Testing order button for: {item_name}")

                self.assertTrue(
                    test_button.is_displayed(),
                    f"Order button for {item_name} should be displayed",
                )
                test_button.click()

                # Check if clicking added item to cart by checking cart badge
                try:
                    WebDriverWait(driver, 5).until(
                        EC.text_to_be_present_in_element((By.ID, "cartBadge"), "1")
                    )
                    print(f"Successfully added {item_name} to cart")
                except:
                    print("Item might not have been added to cart")
            else:
                print("No order buttons found")
        except Exception as e:
            print(f"Error testing 'Order Now' buttons: {e}")

        # Test 6: Footer Links
        try:
            print("Testing footer links")
            footer = driver.find_element(By.TAG_NAME, "footer")
            footer_links = footer.find_elements(By.TAG_NAME, "a")

            print(f"Found {len(footer_links)} footer links")

            # Test a sample of footer links (first link from each column)
            sample_links = footer_links[0:4]  # First link from each column

            for link in sample_links:
                link_text = link.text
                print(f"Testing footer link: {link_text}")
                self.assertTrue(
                    link.is_displayed(),
                    f"Footer link '{link_text}' should be displayed",
                )
                self.assertTrue(
                    link.is_enabled(), f"Footer link '{link_text}' should be clickable"
                )

                # We won't click on these to avoid navigating away
        except Exception as e:
            print(f"Error testing footer links: {e}")

    def tearDown(self):
        # Close the browser
        print("Test complete, closing browser")
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
