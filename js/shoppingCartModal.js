// Arthur Holmes
// 2/18/2025
// Creates a Bootstrap modal for the shopping cart,
// allowing users to view and manage their selected items.
// The modal includes a dynamically updated cart items container,
// a total price display, and a "Clear Cart" button to
// remove all items. It features a close button to exit the
// modal and a "Checkout" button that redirects users to the payment page.
// This modal is hidden
// by default and only appears when the user interacts with the cart icon.

// Wait for the page to fully load before executing the script
document.addEventListener("DOMContentLoaded", function () {
  /* ===========================================
       🛒 DYNAMICALLY CREATE SHOPPING CART MODAL 
       =========================================== */

  // Define the HTML structure of the shopping cart modal as a template string
  const cartModalHTML = `
        <div class="modal fade" id="cartModal" tabindex="-1" aria-labelledby="cartModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">

                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h5 class="modal-title" id="cartModalLabel">Your Shopping Cart</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>

                    <!-- Modal Body (Displays Cart Items Dynamically) -->
                    <div class="modal-body">
                        <div class="cart-items-container">
                            <!-- Cart items will be dynamically inserted here -->
                        </div>
                        <hr>

                        <!-- Cart Total & Clear Cart Button -->
                        <div class="d-flex justify-content-between align-items-center">
                            <h5>Total: <span id="cartTotal">$0.00</span></h5>
                            <button class="btn btn-danger btn-sm" id="clearCart">Clear Cart</button>
                        </div>
                    </div>

                    <!-- Modal Footer (Close & Checkout Buttons) -->
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" onclick="window.location.href='payment.html'"
                            class="btn btn-primary">Checkout</button>
                    </div>

                </div>
            </div>
        </div>`;

  // Append the modal to the document body (so it's not in the main HTML)
  document.body.insertAdjacentHTML("beforeend", cartModalHTML);
});
