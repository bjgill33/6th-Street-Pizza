// Arthur Holmes – Cart Handler (modal + logic)
// Injects cart modal + handles loading, badge update, quantity updates, and rendering logic

// Inject the cart modal HTML into the page
const cartModalHTML = `
<div class="modal fade" id="cartModal" tabindex="-1" aria-labelledby="cartModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="cartModalLabel">Your Cart</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <ul id="cartItems" class="list-group"></ul>
        <div class="mt-3 text-end">
          <strong>Total: $<span id="cartTotal">0.00</span></strong>
        </div>
      </div>
      <div class="modal-footer">
        <a href="/payment/" class="btn btn-primary w-100">Proceed to Checkout</a>
      </div>
    </div>
  </div>
</div>
`;

document.body.insertAdjacentHTML("beforeend", cartModalHTML);

// Define behavior for badge and cart loading
document.addEventListener("DOMContentLoaded", function () {
  const badge = document.getElementById("cartBadge");

  // Fetch Cart Data from Backend and Update UI
  window.fetchCart = async function () {
    try {
      const res = await fetch("/cart/data/", {
        method: "GET",
        credentials: "include",
      });
      const data = await res.json();
      updateCartBadge(data.cart);
      renderCart(data.cart);
    } catch (err) {
      console.error("Failed to load cart:", err);
    }
  };

  // Render Cart Items to Cart Modal
  function renderCart(cart) {
    const list = document.getElementById("cartItems");
    list.innerHTML = "";
    let totalAmount = 0;
    let itemCount = 0;

    for (const key in cart) {
      const item = cart[key];

      const name = item.name || "Unnamed Item";
      const quantity = parseInt(item.quantity) || 0;
      const price = parseFloat(item.price) || 0;
      const toppings = item.toppings || [];
      const size = item.size ? ` (${item.size})` : "";
      const subtotal = price * quantity;

      if (quantity === 0 || isNaN(subtotal)) continue;

      totalAmount += subtotal;
      itemCount += quantity;

      const li = document.createElement("li");
      li.className = "list-group-item";

      li.innerHTML = `
        <div class="d-flex justify-content-between align-items-start w-100">
          <div>
            <strong>${name}</strong>${size}<br>
            <small>Qty:
              <select class="form-select cart-quantity" data-key="${key}" style="width: 60px; display: inline;">
                ${[1, 2, 3, 4, 5].map(q => `
                  <option value="${q}" ${quantity == q ? "selected" : ""}>${q}</option>
                `).join("")}
              </select>
            </small>
            ${Array.isArray(toppings) && toppings.length > 0
              ? `<br><small class="text-muted">Toppings: ${toppings.join(", ")}</small>`
              : ""}
          </div>
          <div class="text-end">
            <span class="item-total" data-key="${key}">$${subtotal.toFixed(2)}</span>
            <button class="btn btn-sm btn-outline-danger mt-1 remove-item" data-key="${key}">
              🗑️
            </button>
          </div>
        </div>
      `;

      list.appendChild(li);
    }

    // Recalculate the cart total and update DOM
    calculateCartTotal(cart);
    updateCartBadge(cart);

    // Add event listeners for item removal
    document.querySelectorAll(".remove-item").forEach(btn => {
      btn.addEventListener("click", async function () {
        const key = this.dataset.key;
        await removeCartItem(key);
      });
    });
  }

  // Listen for Quantity Changes and Update Cart
  document.addEventListener("change", async function (e) {
    if (e.target.classList.contains("cart-quantity")) {
      const itemKey = e.target.dataset.key;
      const newQuantity = parseInt(e.target.value);
      await updateCartQuantity(itemKey, newQuantity);
    }
  });

  // Remove Cart Item
  async function removeCartItem(key) {
    const formData = new FormData();
    formData.append("product_key", key);

    try {
      const res = await fetch("/cart/remove/", {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });
      const data = await res.json();
      if (data.cart) {
        updateCartBadge(data.cart);
        renderCart(data.cart);
      }
    } catch (err) {
      console.error("Error removing item:", err);
    }
  }

  document.getElementById("cartModal").addEventListener("show.bs.modal", fetchCart);
  fetchCart();
});

// Update Cart Quantity via API Call and Re-render
async function updateCartQuantity(itemKey, quantity) {
  try {
    const res = await fetch("/cart/update/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({
        product_key: itemKey,
        quantity: quantity,
      }),
    });

    const data = await res.json();
    if (data.cart) {
      updateCartBadge(data.cart);
      renderCart(data.cart);

      // Update item subtotal dynamically
      const updatedItem = data.cart[itemKey];
      if (updatedItem) {
        const itemTotal = document.querySelector(`.item-total[data-key="${itemKey}"]`);
        if (itemTotal) {
          itemTotal.textContent = `$${(updatedItem.price * updatedItem.quantity).toFixed(2)}`;
        }
      }

      // Recalculate the total
      calculateCartTotal(data.cart);
    } else {
      alert("Failed to update quantity.");
    }
  } catch (err) {
    console.error("Error updating cart:", err);
  }
}

// Handle manual modal open when cart icon is clicked
document.addEventListener("DOMContentLoaded", function () {
  const cartIcon = document.querySelector("[data-bs-target='#cartModal']");
  const modalElement = document.getElementById("cartModal");

  if (cartIcon && modalElement) {
    const modal = new bootstrap.Modal(modalElement);
    cartIcon.addEventListener("click", function (e) {
      e.preventDefault();
      modal.show();
    });
  }
});

// Update cart badge function
function updateCartBadge(cart) {
  const badge = document.getElementById("cartBadge");
  let itemCount = 0;
  for (const key in cart) {
    itemCount += cart[key].quantity;
  }
  badge.textContent = itemCount > 0 ? itemCount : "0";
}

// Recalculate Cart Total and Update DOM
function calculateCartTotal(cart) {
  const total = Object.values(cart).reduce((sum, item) => {
    return sum + item.price * item.quantity;
  }, 0);

  document.getElementById("cartTotal").textContent = total.toFixed(2);
}

// CSRF cookie helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
