// Arthur Holmes
// 2/18/2025
// This script enables users to open the order
// customization modal when they click the "Order Now" button.

// Wait for the DOM to be fully loaded before executing the script
document.addEventListener("DOMContentLoaded", function () {
  // ✅ Select all "Order Now" buttons inside elements with the class "order-card"
  const orderButtons = document.querySelectorAll(".order-card .btn-primary");

  // ✅ Loop through each "Order Now" button and attach a click event listener
  orderButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      event.preventDefault(); // Prevent default link behavior (stops page from navigating)

      // ✅ Create a new Bootstrap modal instance and show it
      let modal = new bootstrap.Modal(document.getElementById("orderModal"));
      modal.show();
    });
  });
});
