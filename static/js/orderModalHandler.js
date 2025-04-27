// Arthur Holmes – 2025-03-21 (Updated for Session-Based Cart Handling)
// Injects modal HTML, handles order button behavior, and submits via fetch to update Django session cart.

// Inject the Order Modal into the DOM
const modalHTML = `
<div class="modal fade" id="orderModal" tabindex="-1" aria-labelledby="orderModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form method="POST">
        ${window.csrfTokenHTML}
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
          <!-- Discount Banner (shown if a discount is active) -->
<div id="modalDiscountBanner" class="alert alert-success mt-3 d-none">
  <strong>Coupon Applied:</strong> <span id="modalDiscountName"></span><br>
  Discount: <span id="modalDiscountPercent"></span>
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
const updateTotal = (triggerButton = null) => {
  const category = document.getElementById("modalCategory").value;
  const qty = parseInt(document.getElementById("modalQuantity").value);
  let sizePrice = 0;
  let toppingTotal = 0;

  if (category === "pizza") {
    const size = document.getElementById("modalSize");
    sizePrice = parseFloat(size.options[size.selectedIndex].dataset.price || 0);

    const toppings = document.getElementById("modalToppings");
    const selectedToppings = [...toppings.selectedOptions];

    if (selectedToppings.length > 3) {
      selectedToppings.forEach(opt => opt.selected = false);
      alert("Only 3 toppings are allowed.");
    } else {
      toppingTotal = selectedToppings.reduce((sum, t) => sum + parseFloat(t.dataset.price || 0), 0);
    }
  } else {
    // Pull price from the data-* attribute of the clicked button (safer and accurate)
    const productId = document.getElementById("modalProductId").value;
    const button = triggerButton || document.querySelector(`.order-btn[data-id='${productId}']`);
    sizePrice = parseFloat(button?.dataset.price || 0);
  }

  const total = qty * (sizePrice + toppingTotal);
  document.getElementById("modalTotal").textContent = isNaN(total) ? "0.00" : total.toFixed(2);

  // Show discount if available
  const discountBanner = document.getElementById("modalDiscountBanner");

  if (window.appliedDiscount && discountBanner) {
    const discountAmount = (total * window.appliedDiscount.percentage) / 100;
    const discountedTotal = total - discountAmount;

    document.getElementById("modalDiscountName").textContent = window.appliedDiscount.name;
    document.getElementById("modalDiscountPercent").textContent = `-${discountAmount.toFixed(2)} (${window.appliedDiscount.percentage}%)`;
    document.getElementById("modalTotal").textContent = discountedTotal.toFixed(2);
    discountBanner.classList.remove("d-none");
  } else if (discountBanner) {
    discountBanner.classList.add("d-none");
  }

};

  // Capitalize function for data-price lookup
  function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
  }


  // Populate the modal and display it when the order button is clicked
orderButtons.forEach(button => {
  button.addEventListener("click", function (e) {
    e.preventDefault();

    const name = this.dataset.name;
    const category = this.dataset.category;
    const defaultSize = this.dataset.defaultSize || "small";

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

      modalSize.innerHTML = `
        <option value="small" data-price="${this.dataset.priceSmall}" ${defaultSize === "small" ? "selected" : ""}>Small ($${this.dataset.priceSmall})</option>
        <option value="medium" data-price="${this.dataset.priceMedium}" ${defaultSize === "medium" ? "selected" : ""}>Medium ($${this.dataset.priceMedium})</option>
        <option value="large" data-price="${this.dataset.priceLarge}" ${defaultSize === "large" ? "selected" : ""}>Large ($${this.dataset.priceLarge})</option>
        <option value="extra_large" data-price="${this.dataset.priceExtraLarge}" ${defaultSize === "extra_large" ? "selected" : ""}>Extra Large ($${this.dataset.priceExtraLarge})</option>
      `;

      modalToppings.innerHTML = (window.toppingsList || []).map(t =>
        `<option value="${t.name}" data-price="${t.price}">${t.name} ($${t.price})</option>`
      ).join("");

      modalSize.addEventListener("change", () => updateTotal(this));
      modalToppings.addEventListener("change", () => updateTotal(this));
      document.getElementById("modalQuantity").addEventListener("change", () => updateTotal(this));
    } else {
      sizeContainer.style.display = "none";
      toppingsContainer.style.display = "none";
      modalSize.innerHTML = "";
      modalToppings.innerHTML = "";
    }

    updateTotal(this);
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


