## Manual Navigation Testing

### Test Case: Verify that all links and navigation buttons work.

#### From `index.html`

1. **Menu Button**:
   - **Action**: Click the "Menu" button from the home page.
   - **Expected Result**: Successful navigation to `menu.html`.
   - **Back Button**: Clicking the back button returns the user to `index.html`.

2. **Locations Button**:
   - **Action**: Click the "Locations" button.
   - **Expected Result**: Currently does nothing.

3. **Coupons Button**:
   - **Action**: Click the "Coupons" button.
   - **Expected Result**: Currently does nothing.

4. **Rewards Button**:
   - **Action**: Click the "Rewards" button.
   - **Expected Result**: Currently does nothing.

5. **Tracker Button**:
   - **Action**: Click the "Tracker" button.
   - **Expected Result**: Currently does nothing.

6. **Cart Button**:
   - **Scenario 1**: Cart is empty.
     - **Action**: Click the "Cart" button.
     - **Expected Result**: A pop-up window displays "Your cart is currently empty" with three options:
       1. **X Button**: Closes the pop-up.
       2. **Close Button**: Closes the pop-up.
       3. **Checkout Button**: Navigates the user to `payment.html`.
     - **Suggestion**: Disable the "Checkout" button when the cart is empty.
   - **Scenario 2**: Cart contains an item.
     - **Action**: Click the "Cart" button.
     - **Expected Result**: The pop-up window displays "Your cart is currently empty". Clicking the "Checkout" button navigates the user to `payment.html`, but the item in the cart is possibly removed (red count resets to zero).

7. **Delivery Button**:
   - **Action**: Click the "Delivery" button.
   - **Expected Result**: A "Delivery Details" pop-up window appears.
   - **Suggestion**: Navigate the user to `menu.html` on click and ask for delivery details at checkout.

8. **Carryout Button**:
   - **Action**: Click the "Carryout" button.
   - **Expected Result**: A "Select a Location" pop-up window appears. Currently, locations cannot be selected. The "X" and "Close" buttons close the window.

9. **6th Street Pizza Logo Button**:
   - **Action**: Click the logo button.
   - **Expected Result**:
     - From `index.html`: No action (user is already on `index.html`).
     - From `menu.html` or `payment.html`: Successful navigation back to `index.html`.
   - **Suggestion**: Disable the logo button when the user is already on `index.html`.

---

### Suggestions for Improvement
1. **Cart Button**:
   - Disable the "Checkout" button when the cart is empty to prevent confusion.
2. **Delivery Button**:
   - Navigate the user to `menu.html` on click and collect delivery details during checkout.
3. **6th Street Pizza Logo Button**:
   - Disable the button when the user is on `index.html` to avoid redundancy.