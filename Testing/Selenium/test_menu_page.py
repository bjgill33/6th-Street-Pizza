def test_menu_page(self):
        """Test if the menu page loads correctly"""
        print("Navigating to menu page...")
        self.driver.get("http://127.0.0.1:5500/menu.html")
        menu_header = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertEqual(menu_header.text.strip().lower(), "menu",
                         "Menu header not found or incorrect!")
        print("Test Passed! Menu heading found")

    def test_menu_categories(self):
        """Test clicking menu categories in the dropdown"""
        driver = self.driver

        # Add print statement for debugging
        print("Waiting for filter button to be clickable...")

        try:
            # Increased wait time and used XPath for better flexibility
            filter_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@id='menuFilter']"))
            )

            # Check if it's visible and clickable
            if filter_button.is_displayed() and filter_button.is_enabled():
                filter_button.click()
                print("Filter button clicked")
            else:
                print("Filter button is not clickable or visible")

            # Wait for the dropdown menu to appear
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

                # Trigger filtering directly
                driver.execute_script(f"filterMenu('{category_name.lower()}')")

                # Wait for menu items to load based on the category
                self.wait_for_menu_items(category_name)

                print(f"Test Passed! Menu items loaded for {category_name}!")

                # Re-open the dropdown for the next category selection
                filter_button.click()
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "ul.dropdown-menu"))
                )
                time.sleep(1)

            print("All categories clicked and verified successfully!")

        except Exception as e:
            print(f"Error occurred while interacting with filter button: {e}")
            print(driver.page_source)  # Output the page source for debugging
            self.fail(
                "Test failed due to an issue with filter button or category interaction")

    def wait_for_menu_items(self, category_name):
        """Helper function to wait for the corresponding menu items based on category"""
        category_css = {
            'pizza': ".pizza .card",
            'wings': ".wings .card",
            'dessert': ".dessert .card",
            'drinks': ".drinks .card"
        }.get(category_name.lower(), ".card")

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, category_css))
        )
