// ============================
// DISCOUNT HANDLER SCRIPT
// ============================
document.addEventListener("DOMContentLoaded", function () {

  // ==========================
  // DOM Element References
  // ==========================
  const discountField = document.getElementById("discountCode");              // Input for discount code
  const clearBtn = document.getElementById("clearDiscountBtn");              // Button to clear discount
  const orderTotal = document.getElementById("orderTotal");                   // Total price element
  const notice = document.getElementById("discountNotice");                   // Discount notice alert
  const appliedName = document.getElementById("appliedCouponName");          // Name of applied coupon
  const appliedAmount = document.getElementById("appliedDiscountAmount");    // Displayed discount amount

  let baseTotal = 0;

  // ========================================================
  // Function: updateCartWithDiscount(code)
  // - Fetches coupon info from server
  // - Updates total display and discount message
  // ========================================================
  function updateCartWithDiscount(code) {
    if (!code.trim()) {
      notice.style.display = "none";
      appliedName.textContent = "";
      appliedAmount.textContent = "";
      orderTotal.textContent = `$${baseTotal.toFixed(2)}`;
      return;
    }

    fetch(`/validate-coupon/?code=${encodeURIComponent(code)}`, {
      method: "GET",
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        if (data.valid) {
          const discountValue = (baseTotal * data.percentage) / 100;
          const finalPrice = baseTotal - discountValue;

          notice.style.display = "block";
          appliedName.textContent = data.name;
          appliedAmount.textContent = `-${discountValue.toFixed(2)} (${data.percentage}%)`;
          orderTotal.textContent = `$${finalPrice.toFixed(2)}`;
        } else {
          notice.style.display = "none";
          appliedName.textContent = "";
          appliedAmount.textContent = "";
          orderTotal.textContent = `$${baseTotal.toFixed(2)}`;
        }
      })
      .catch(err => {
        console.error("Error validating coupon:", err);
        notice.style.display = "none";
        appliedName.textContent = "";
        appliedAmount.textContent = "";
        orderTotal.textContent = `$${baseTotal.toFixed(2)}`;
      });
  }

  // ========================================================
  // Event: Apply discount on blur
  // ========================================================
  if (discountField) {
    discountField.addEventListener("blur", () => {
      updateCartWithDiscount(discountField.value);
    });
  }

  // ========================================================
  // Event: Clear discount with button
  // ========================================================
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      fetch("/clear-coupon/", { method: "POST", credentials: "include" })
        .then(() => {
          discountField.value = "";
          notice.style.display = "none";
          appliedName.textContent = "";
          appliedAmount.textContent = "";
          orderTotal.textContent = `$${baseTotal.toFixed(2)}`;
        })
        .catch(err => console.error("Failed to clear discount:", err));
    });
  }

  // ========================================================
  // Initial Load: Fetch cart and restore discount from session
  // ========================================================
  fetch("/cart/data/", {
    method: "GET",
    credentials: "include"
  })
    .then(res => res.json())
    .then(data => {
      const cart = data.cart || {};
      baseTotal = Object.values(cart).reduce((sum, item) => {
        return sum + parseFloat(item.price) * item.quantity;
      }, 0);

      // Reapply saved discount if available
      if (window.appliedDiscount) {
        const { name, percentage } = window.appliedDiscount;
        const discountValue = (baseTotal * percentage) / 100;
        const finalPrice = baseTotal - discountValue;

        notice.style.display = "block";
        appliedName.textContent = name;
        appliedAmount.textContent = `-${discountValue.toFixed(2)} (${percentage}%)`;
        orderTotal.textContent = `$${finalPrice.toFixed(2)}`;
      } else {
        orderTotal.textContent = `$${baseTotal.toFixed(2)}`;
      }
    });
});
