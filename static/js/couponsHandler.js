// Wait until the entire page has loaded
document.addEventListener("DOMContentLoaded", function () {
  const totalElement = document.getElementById("orderTotal");
  const notice = document.getElementById("discountNotice");
  const appliedName = document.getElementById("appliedCouponName");
  const appliedAmount = document.getElementById("appliedDiscountAmount");
  const clearBtn = document.getElementById("clearDiscountBtn");

  let baseTotal = 0;
  let appliedButton = null;

  // Fetch the current cart data from the backend
  fetch("/cart/data/", {
    method: "GET",
    credentials: "include"
  })
    .then(res => res.json())
    .then(data => {
      const cart = data.cart || {};
      baseTotal = Object.values(cart).reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0);

      if (window.appliedDiscount && window.appliedDiscount.percentage) {
        const discountValue = (baseTotal * window.appliedDiscount.percentage) / 100;
        const newTotal = baseTotal - discountValue;
        totalElement.textContent = `$${newTotal.toFixed(2)}`;
        if (notice) notice.style.display = "block";
        if (appliedName) appliedName.textContent = window.appliedDiscount.name;
        if (appliedAmount) appliedAmount.textContent = `-${discountValue.toFixed(2)} (${window.appliedDiscount.percentage}%)`;
      } else {
        totalElement.textContent = `$${baseTotal.toFixed(2)}`;
      }
    });

  // Set up event listeners for all "Apply Discount" buttons
  document.querySelectorAll(".apply-btn").forEach(button => {
    button.addEventListener("click", () => {
      const code = button.dataset.code;

      fetch(`/validate-coupon/?code=${encodeURIComponent(code)}`, {
        method: "GET",
        credentials: "include"
      })
        .then(res => res.json())
        .then(data => {
          if (data.valid) {
            const discountValue = (baseTotal * data.percentage) / 100;
            const newTotal = baseTotal - discountValue;

            totalElement.textContent = `$${newTotal.toFixed(2)}`;

            // If a discount banner already exists, update it
            if (notice) {
              notice.classList.remove("alert-warning");
              notice.classList.add("alert-success");
              notice.innerHTML = `
                <strong>Coupon Applied:</strong> <span id="appliedCouponName">${data.name}</span><br>
                Discount: <span id="appliedDiscountAmount">-${discountValue.toFixed(2)} (${data.percentage}%)</span><br>
                <button class="btn btn-sm btn-outline-danger mt-2" id="clearDiscountBtn">Clear Coupon</button>
              `;
              notice.style.display = "block";

              // Rebind Clear Coupon Button
              const newClearBtn = document.getElementById("clearDiscountBtn");
              if (newClearBtn) {
                newClearBtn.addEventListener("click", () => {
                  fetch("/clear-coupon/", {
                    method: "POST",
                    credentials: "include",
                    headers: {
                      "X-CSRFToken": getCookie("csrftoken"),
                    }
                  })
                    .then(res => res.json())
                    .then(data => {
                      if (data.cleared) {
                        window.location.reload();
                      }
                    })
                    .catch(err => console.error("Failed to clear discount:", err));
                });
              }
            }

            // Button behavior
            if (appliedButton) {
              appliedButton.disabled = false;
              appliedButton.textContent = "Apply Discount";
            }
            button.disabled = true;
            button.textContent = "Coupon Applied";
            appliedButton = button;
          } else {
            alert(data.error || "Invalid coupon");
          }
        })
        .catch(err => console.error("Apply coupon failed:", err));
    });
  });
});

// Helper function to get CSRF token
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
