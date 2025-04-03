// Arthur Holmes – 2025-03-21 (Updated for Session-Based Cart Handling)
// Injects modal HTML, handles order button behavior, and submits via fetch to update Django session cart.

// Inject the Order Modal into the DOM
const modalHTML = `
<div class="modal fade" id="orderModal" tabindex="-1" aria-labelledby="orderModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="POST">
        ${window.csrfTokenHTML}  // CSRF Token for security (Django integration)
        <div class="modal-header">
          <h5 class="modal-title" id="orderModalLabel">Customize Your Order</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body">
          <!-- Selected item name display -->
          <h6 id="modalItemTitle" class="fw-bold text-primary mb-3"></h6>
          <input type="hidden" name="name" id="modalName" />
          <input type="hidden" name="category" id="modalCategory" />
          <input type="hidden" name="product_id" id="modalProductId" />

          <!-- Pizza size selector, hidden unless it's a pizza -->
          <div id="sizeContainer" style="display:none;">
            <label for="size">Select Size</label>
            <select class="form-select" name="size" id="modalSize"></select>
          </div>

          <!-- Toppings selector, hidden unless it's a pizza -->
          <div id="toppingsContainer" style="display:none;">
            <label for="toppings">Extra Toppings</label>
            <select class="form-select" name="toppings" id="modalToppings" multiple></select>
            <small class="text-muted">Limit: 3 toppings</small>
          </div>

          <!-- Quantity selector with preset options -->
          <label for="quantity" class="mt-3">Quantity</label>
          <select class="form-select" name="quantity" id="modalQuantity">
            ${[1, 2, 3, 4, 5].map(i => `<option value="${i}">${i}</option>`).join("")}
          </select>

          <!-- Total Price Display -->
          <div class="mt-3">
            <strong>Total:</strong> $<span id="modalTotal">0.00</span>
          </div>
        </div>

        <div class="modal-footer">
          <button type="submit" class="btn btn-success w-100">Add to Cart</button>
        </div>
      </form>
    </div>
  </div>
</div>`;
document.body.insertAdjacentHTML("beforeend", modalHTML);

// Bootstrap Modal Setup and Order Button Handling
document.addEventListener("DOMContentLoaded", function () {
  const modal = new bootstrap.Modal(document.getElementById("orderModal"));
  const orderButtons = document.querySelectorAll(".order-btn");

  // Function to update the total price based on selected size, quantity, and toppings
  const updateTotal = () => {
    const category = document.getElementById("modalCategory").value;
    const qty = parseInt(document.getElementById("modalQuantity").value);
    let sizePrice = 0;
    let toppingTotal = 0;

    // Calculate size price and topping price if the item is a pizza
    if (category === "pizza") {
      const size = document.getElementById("modalSize");
      sizePrice = parseFloat(size.options[size.selectedIndex].dataset.price || 0);

      const toppings = document.getElementById("modalToppings");
      const selectedToppings = [...toppings.selectedOptions];

      // Ensure no more than 3 toppings are selected
      if (selectedToppings.length > 3) {
        selectedToppings.forEach(opt => opt.selected = false);
        alert("Only 3 toppings are allowed.");
      } else {
        toppingTotal = selectedToppings.reduce((sum, t) => sum + parseFloat(t.dataset.price || 0), 0);
      }
    } else {
      // Non-pizza items use a simple size price from the button dataset
      const productId = document.getElementById("modalProductId").value;
      const targetBtn = document.querySelector(`.order-btn[data-id='${productId}']`);
      sizePrice = parseFloat(targetBtn?.dataset.price || 0);
    }

    // Calculate and update total
    const total = qty * (sizePrice + toppingTotal);
    document.getElementById("modalTotal").textContent = isNaN(total) ? "0.00" : total.toFixed(2);
  };

  // Populate the modal and display it when the order button is clicked
  orderButtons.forEach(button => {
    button.addEventListener("click", function (e) {
      e.preventDefault();

      const name = this.dataset.name;
      const category = this.dataset.category;

      document.getElementById("modalName").value = name;
      document.getElementById("modalCategory").value = category;
      document.getElementById("modalItemTitle").textContent = name;
      document.getElementById("modalProductId").value = this.dataset.id;

      const sizeContainer = document.getElementById("sizeContainer");
      const toppingsContainer = document.getElementById("toppingsContainer");
      const modalSize = document.getElementById("modalSize");
      const modalToppings = document.getElementById("modalToppings");

      if (category === "pizza") {
        sizeContainer.style.display = "block";
        toppingsContainer.style.display = "block";

        // Populate size options with corresponding prices
        modalSize.innerHTML = `
          <option value="small" data-price="${this.dataset.priceSmall}">Small ($${this.dataset.priceSmall})</option>
          <option value="medium" data-price="${this.dataset.priceMedium}">Medium ($${this.dataset.priceMedium})</option>
          <option value="large" data-price="${this.dataset.priceLarge}">Large ($${this.dataset.priceLarge})</option>
          <option value="extra_large" data-price="${this.dataset.priceExtraLarge}">Extra Large ($${this.dataset.priceExtraLarge})</option>
        `;

        // Populate toppings using global data
        modalToppings.innerHTML = (window.toppingsList || []).map(t =>
          `<option value="${t.name}" data-price="${t.price}">${t.name} ($${t.price})</option>`
        ).join("");

        // Track changes to size, toppings and quantity
        modalSize.addEventListener("change", updateTotal);
        modalToppings.addEventListener("change", updateTotal);
        document.getElementById("modalQuantity").addEventListener("change", updateTotal);

      } else {
        sizeContainer.style.display = "none";
        toppingsContainer.style.display = "none";
        modalSize.innerHTML = "";
        modalToppings.innerHTML = "";
      }

      updateTotal();
      modal.show();
    });
  });

  // Handle form submission using fetch to add items to the cart
  document.querySelector("#orderModal form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Convert selected toppings to JSON
    const toppingsEl = document.getElementById("modalToppings");
    if (toppingsEl) {
      const toppings = Array.from(toppingsEl.selectedOptions).map(opt => opt.value);
      formData.append("toppings_json", JSON.stringify(toppings));
    }

    try {
      const res = await fetch("/cart/add/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData,
      });

      const data = await res.json();
      if (data.cart) {
        updateCartBadge(data.cart);
        bootstrap.Modal.getInstance(document.getElementById("orderModal")).hide();
      } else {
        alert("Failed to add to cart.");
      }
    } catch (err) {
      console.error("Add to cart error:", err);
      alert("There was an error.");
    }
  });
});

// Retrieve CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(cookie => {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.split("=")[1]);
      }
    });
  }
  return cookieValue;
}

// Update the cart badge with the correct item count
function updateCartBadge(cart) {
  const badge = document.getElementById("cartBadge");
  let itemCount = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
  badge.textContent = itemCount;
}


