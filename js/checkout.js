// Arthur Holmes
// 2/18/2025
// This script ensures the "Review Your Order" section dynamically updates based on cart contents.

// Wait for the DOM to be fully loaded before executing the script
document.addEventListener("DOMContentLoaded", function () {
  updateOrderReview();
});

/* ===========================
   🛒 UPDATE ORDER REVIEW  
   =========================== */
function updateOrderReview() {
  const cart = JSON.parse(localStorage.getItem("cart")) || []; // Retrieve cart data from localStorage
  const orderReviewContainer = document.querySelector(".col-md-4 .card"); // Target the order review card
  let orderHTML = "";
  let subtotal = 0;

  if (cart.length === 0) {
    orderHTML = `<p>Your cart is empty.</p>`;
  } else {
    cart.forEach((item, index) => {
      let itemTotal = item.price * item.quantity;
      subtotal += itemTotal;
      orderHTML += `
                <p><strong>Item:</strong> ${item.name}</p>
                <p><strong>Price:</strong> $${item.price.toFixed(2)}</p>
                <p><strong>Qty:</strong> ${item.quantity}</p>
                <p><strong>Subtotal:</strong> $${itemTotal.toFixed(2)}</p>
                <hr>
            `;
    });

    // Calculate tax (Assuming 8% sales tax)
    let tax = subtotal * 0.08;
    let total = subtotal + tax;

    // Append totals
    orderHTML += `
            <p><strong>Subtotal:</strong> $${subtotal.toFixed(2)}</p>
            <p><strong>Delivery:</strong> Free (5-10 business days)</p>
            <p><strong>Tax:</strong> $${tax.toFixed(2)}</p>
            <p><strong>Total:</strong> $${total.toFixed(2)}</p>
            <div class="d-flex gap-3">
                <button class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#cartModal">Edit</button>
                <a href="menu.html" class="btn btn-primary">Add More</a>
            </div>
        `;
  }

  orderReviewContainer.innerHTML = orderHTML;
}
