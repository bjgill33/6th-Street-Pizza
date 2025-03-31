// Arthur Holmes
// 2/18/2025
// Waits for the page to fully load using the DOMContentLoaded event, stores
// the modal structure as a template string, dynamically appends the modal to the document
// body, and ensures all modals are managed within JavaScript to keep the HTML clean and uncluttered.
// Wait for the page to fully load before executing the script
document.addEventListener("DOMContentLoaded", function () {
  /* ===========================================
       🍕 DYNAMICALLY CREATE ORDER CUSTOMIZATION MODAL 
       =========================================== */

  // Define the HTML structure of the order modal as a template string
  const orderModalHTML = `
        <div class="modal fade" id="orderModal" tabindex="-1" aria-labelledby="orderModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">

                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h5 class="modal-title" id="orderModalLabel">Customize Your Pizza</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>

                    <!-- Modal Body (Customization Options) -->
                    <div class="modal-body">
                        <form id="customizeForm">

                            <!-- Hidden Field for Selected Item -->
                            <input type="hidden" id="selectedItemId">

                            <!-- Display Selected Item Name & Price -->
                            <h5 id="selectedItemName"></h5>
                            <p id="selectedItemPrice"></p>

                            <!-- Pizza Size Selection -->
                            <label for="size">Select Size:</label>
                            <select id="size" class="form-select">
                                <option value="small" data-price="0">Small</option>
                                <option value="medium" data-price="2">Medium (+$2.00)</option>
                                <option value="large" data-price="4">Large (+$4.00)</option>
                            </select>

                            <!-- Quantity Selection -->
                            <label for="quantity" class="mt-3">Select Quantity:</label>
                            <select id="quantity" class="form-select">
                                <option value="1">1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                            </select>

                            <!-- Extra Toppings Selection -->
                            <h6 class="mt-3">Extra Toppings ($0.25 each):</h6>
                            <div class="form-check">
                                <input class="form-check-input topping" type="checkbox" value="Onions" data-price="0.25">
                                <label class="form-check-label">Onions</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input topping" type="checkbox" value="Extra Cheese" data-price="0.25">
                                <label class="form-check-label">Extra Cheese</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input topping" type="checkbox" value="Sausage" data-price="0.25">
                                <label class="form-check-label">Sausage</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input topping" type="checkbox" value="Extra Pepperoni" data-price="0.25">
                                <label class="form-check-label">Extra Pepperoni</label>
                            </div>

                            <!-- Total Price Display -->
                            <h5 class="mt-3">Total: <span id="totalPrice">$0.00</span></h5>

                            <!-- Add to Cart Button -->
                            <button type="button" class="btn btn-success w-100 mt-3" id="addToCartBtn">Add to Cart</button>

                        </form>
                    </div>

                </div>
            </div>
        </div>`;

  // Append the modal to the document body (so it's not in the main HTML)
  document.body.insertAdjacentHTML("beforeend", orderModalHTML);
});
