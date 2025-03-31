// Arthur Holmes
// 2/18/2025
// Waits for the page to fully load before executing
// (DOMContentLoaded event), then creates the Bootstrap modal
// as a string instead of embedding it in the HTML.
// The modal includes dynamically updated item name and
//  price placeholders, a size selection dropdown
// (small, medium, large), a quantity selection dropdown
// (1-5 items), checkboxes for extra toppings
// (each costing $0.25), a total price display that
// updates dynamically, and an "Add to Cart" button.
//  Finally, the modal is inserted into the
// document body using JavaScript.

// ✅ Create the modal HTML structure as a string
const orderModalHTML = `
        <div class="modal fade" id="orderModal" tabindex="-1" aria-labelledby="orderModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="orderModalLabel">Customize Your Pizza</h5>  <!-- Modal title -->
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>  <!-- Close button -->
                    </div>
                    <div class="modal-body">
                        <form id="customizeForm">  <!-- Form for customizing the pizza order -->
                            <input type="hidden" id="selectedItemId">  <!-- Hidden input to store selected item ID -->

                            <h5 id="selectedItemName"></h5>  <!-- Placeholder for the selected item name -->
                            <p id="selectedItemPrice"></p>  <!-- Placeholder for the selected item price -->

                            <!-- 🍕 Pizza Size Selection -->
                            <label id="sizeLabel" for="size">Select Size:</label>
                            <select id="size" class="form-select">
                                <option value="small" data-price="0">Small</option>  <!-- Base price (no extra cost) -->
                                <option value="medium" data-price="2">Medium (+$2.00)</option>  <!-- Medium size adds $2 -->
                                <option value="large" data-price="4">Large (+$4.00)</option>  <!-- Large size adds $4 -->
                            </select>

                            <!-- 🔢 Quantity Selection -->
                            <label id="quantityLabel" for="quantity" class="mt-3">Select Quantity:</label>
                            <select id="quantity" class="form-select">
                                <option value="1">1</option>  <!-- Default quantity: 1 -->
                                <option value="2">2</option>  <!-- Option for 2 -->
                                <option value="3">3</option>  <!-- Option for 3 -->
                                <option value="4">4</option>  <!-- Option for 4 -->
                                <option value="5">5</option>  <!-- Option for 5 -->
                            </select>

                            <!-- 🧀 Extra Toppings -->
                            <h6 id="toppingsLabel" class="mt-3">Extra Toppings ($0.25 each):</h6>
                            <div class="form-check">
                                <input id="onionsCheckbox" class="form-check-input topping" type="checkbox" value="Onions" data-price="0.25">  <!-- Topping: Onions -->
                                <label id="onionsLabel" class="form-check-label">Onions</label>
                            </div>
                            <div class="form-check">
                                <input id="extraCheeseCheckbox" class="form-check-input topping" type="checkbox" value="Extra Cheese" data-price="0.25">  <!-- Topping: Extra Cheese -->
                                <label id="extraCheeseLabel" class="form-check-label">Extra Cheese</label>
                            </div>
                            <div class="form-check">
                                <input id="sausageCheckbox" class="form-check-input topping" type="checkbox" value="Sausage" data-price="0.25">  <!-- Topping: Sausage -->
                                <label id="sausageLabel" class="form-check-label">Sausage</label>
                            </div>
                            <div class="form-check">
                                <input id="extraPepperoniCheckbox" class="form-check-input topping" type="checkbox" value="Extra Pepperoni" data-price="0.25">  <!-- Topping: Extra Pepperoni -->
                                <label id="extraPepperoniLabel" class="form-check-label">Extra Pepperoni</label>
                            </div>

                            <h5 id="totalPriceLabel" class="mt-3">Total: <span id="totalPrice">$0.00</span></h5>  <!-- Display total price dynamically -->

                            <!-- 🛒 Add to Cart Button -->
                            <button  type="button" class="btn btn-success w-100 mt-3" id="addToCartBtn">Add to Cart</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;

// ✅ Append the modal to the body of the document
document.body.insertAdjacentHTML("beforeend", orderModalHTML); // Dynamically injects the modal into the page
