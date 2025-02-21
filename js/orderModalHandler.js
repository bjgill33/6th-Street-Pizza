// 2/18/2025
// Arthur Holmes
// Wait for the DOM to be fully loaded before executing the script
document.addEventListener("DOMContentLoaded", function () {
  /* ================================
       🛒 ADD TO CART BUTTON HANDLER 
       ================================ */

  // Select the "Add to Cart" button
  const addToCartBtn = document.getElementById("addToCartBtn");

  // Check if the button exists before attaching an event listener
  if (addToCartBtn) {
    addToCartBtn.addEventListener("click", function () {
      // ✅ Close the order customization modal after adding to cart
      let orderModalElement = document.getElementById("orderModal");

      // ✅ Get the Bootstrap modal instance of the "orderModal"
      let orderModalInstance = bootstrap.Modal.getInstance(orderModalElement);

      // If the modal instance does not exist, create a new one
      if (!orderModalInstance) {
        orderModalInstance = new bootstrap.Modal(orderModalElement);
      }

      // ✅ Close the modal window
      orderModalInstance.hide();
    });
  }
});
