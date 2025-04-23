6th-Street-Pizzaawsadmin@fedora02:~/Documents/GitHub/6th-Street-Pizza$ python -m unittest /home/awsadmin/Documents/GitHub/6th-Street-Pizza/testing/Selenium/test_selenium_index.py
Page title: 6th Street Pizza
Location modal appeared as expected
Found 3 location buttons
Selected location: STORE 1
123 MAIN ST, RALEIGH, NC 27601
(919) 555-1234
Location modal closed
Testing navigation link: Menu
Successfully navigated to http://127.0.0.1:8000/menu/
Testing navigation link: Locations
Error testing navigation link 'Locations': Message:

Testing navigation link: Coupons
Successfully navigated to http://127.0.0.1:8000/coupons/
Testing navigation link: Tracker
Error testing navigation link 'Tracker': Message:

Testing cart button
Cart modal appeared successfully

Testing 'Delivery' button with default form values
Error testing delivery button with default values: Message: no such element: Unable to locate element: {"method":"xpath","selector":"//button[@data-bs-target='#deliveryModal']"}
(Session info: chrome=135.0.7049.114); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
Stacktrace:
#0 0x55d59885275a <unknown>
#1 0x55d5983054b0 <unknown>
#2 0x55d5983569b3 <unknown>
#3 0x55d598356ba1 <unknown>
#4 0x55d5983a51f4 <unknown>
#5 0x55d59837c5bd <unknown>
#6 0x55d5983a25e0 <unknown>
#7 0x55d59837c363 <unknown>
#8 0x55d598348d63 <unknown>
#9 0x55d5983499c1 <unknown>
#10 0x55d598817a6b <unknown>
#11 0x55d59881b951 <unknown>
#12 0x55d5987ffb62 <unknown>
#13 0x55d59881c4c4 <unknown>
#14 0x55d5987e413f <unknown>
#15 0x55d5988406f8 <unknown>
#16 0x55d5988408d6 <unknown>
#17 0x55d5988515a6 <unknown>
#18 0x7fe587ed9fa8 start_thread
#19 0x7fe587f5dfcc \_\_clone3

Testing 'Order Now' buttons on food items
No order buttons found
Testing footer links
Found 0 footer links
Test complete, closing browser
.

---

Ran 1 test in 27.001s

OK
6th-Street-Pizzaawsadmin@fedora02:~/Documents/GitHub/6th-Street-Pizza$
