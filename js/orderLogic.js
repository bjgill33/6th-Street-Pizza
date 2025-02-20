// Arthur Holmes
// 2/18/2025
// This script enables users to customize their order when they click
// "Order Now", dynamically updates the total price based on selections,
// extracts item data from hidden fields, and ensures smooth modal interactions.

// Wait for the DOM to be fully loaded before executing the script
document.addEventListener("DOMContentLoaded", function () {
  let secondaryItemData = null; // Stores the secondary item for later addition

  /* =======================  
       🛒 ORDER NOW BUTTON HANDLER  
       ======================= */

  // Select all "Order Now" buttons inside elements with the class "order-card"
  const orderButtons = document.querySelectorAll(".order-card .btn-primary");

  // Loop through each "Order Now" button and attach a click event listener
  orderButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      event.preventDefault(); // Prevent default link behavior (stops page from navigating)

      // ✅ Get the selected item's card
      const card = button.closest(".order-card");

      // ✅ Get all hidden input fields inside the card
      const hiddenFields = card.querySelectorAll("input[type='hidden']");

      // ✅ Extract the primary item's name and price from the first hidden field
      let primaryItemData = hiddenFields[0]?.name.split("$");
      let primaryItemName = primaryItemData[0].trim();
      let primaryItemPrice = parseFloat(primaryItemData[1]);
      let category = hiddenFields[0].value; // "pizza", "chicken", "dessert", or "drink"

      // ✅ Populate the modal with primary item data
      document.getElementById("selectedItemName").textContent = primaryItemName;
      document.getElementById(
        "selectedItemPrice"
      ).textContent = `Base Price: $${primaryItemPrice.toFixed(2)}`;
      document.getElementById("totalPrice").textContent = `$${primaryItemPrice.toFixed(2)}`;
      document.getElementById("orderModal").setAttribute("data-base-price", primaryItemPrice);

      // ✅ Show/hide customization options based on item type
      toggleCustomizationOptions(category);

      // ✅ Store secondary item data if it exists
      secondaryItemData = hiddenFields.length > 1 ? hiddenFields[1]?.name.split("$") : null;

      // ✅ Open the Bootstrap modal
      let modal = new bootstrap.Modal(document.getElementById("orderModal"));
      modal.show();
    });
  });

  /* ============================  
       🍕 SHOW/HIDE CUSTOMIZATION OPTIONS FOR NON-PIZZA ITEMS  
       ============================ */
  function toggleCustomizationOptions(category) {
    const sizeLabel = document.getElementById("sizeLabel");
    const sizeSelect = document.getElementById("size");
    const toppingsLabel = document.getElementById("toppingsLabel");
    const toppingsCheckboxes = document.querySelectorAll(".topping");
    const modalTitle = document.getElementById("orderModalLabel");

    if (category !== "pizza") {
      sizeLabel.style.display = "none"; // Hide size label
      sizeSelect.style.display = "none"; // Hide size dropdown
      toppingsLabel.style.display = "none"; // Hide extra toppings text
      toppingsCheckboxes.forEach((checkbox) => (checkbox.parentElement.style.display = "none")); // Hide topping checkboxes
      modalTitle.textContent = "Select Quantity"; // Change modal title
    } else {
      sizeLabel.style.display = "block"; // Show size label
      sizeSelect.style.display = "block"; // Show size dropdown
      toppingsLabel.style.display = "block"; // Show extra toppings text
      toppingsCheckboxes.forEach((checkbox) => (checkbox.parentElement.style.display = "block")); // Show topping checkboxes
      modalTitle.textContent = "Customize Your Pizza"; // Restore modal title
    }
  }

  /* ============================  
       🏷️ UPDATE TOTAL PRICE DYNAMICALLY  
       ============================ */
  const sizeSelect = document.getElementById("size");
  const toppingsCheckboxes = document.querySelectorAll(".topping");

  function updateTotalPrice() {
    let basePrice = parseFloat(
      document.getElementById("orderModal").getAttribute("data-base-price")
    );
    let sizePrice = parseFloat(sizeSelect.options[sizeSelect.selectedIndex].dataset.price);
    let toppingsCost = 0;

    toppingsCheckboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        toppingsCost += parseFloat(checkbox.dataset.price);
      }
    });

    let quantity = parseInt(document.getElementById("quantity").value);
    let totalPrice = (basePrice + sizePrice + toppingsCost) * quantity;
    document.getElementById("totalPrice").textContent = `$${totalPrice.toFixed(2)}`;
  }

  sizeSelect.addEventListener("change", updateTotalPrice);
  toppingsCheckboxes.forEach((checkbox) => checkbox.addEventListener("change", updateTotalPrice));
  document.getElementById("quantity").addEventListener("change", updateTotalPrice);

  /* ============================  
       🛒 ADD TO CART BUTTON HANDLER  
       ============================ */
  document.getElementById("addToCartBtn").addEventListener("click", function () {
    let primaryName = document.getElementById("selectedItemName").textContent;
    let primaryPrice = parseFloat(
      document.getElementById("orderModal").getAttribute("data-base-price")
    );
    let quantity = parseInt(document.getElementById("quantity").value);

    addItemToCart(primaryName, primaryPrice, quantity);

    // ✅ Add the second item **ONLY IF IT EXISTS** when "Add to Cart" is clicked
    if (secondaryItemData) {
      let secondaryName = secondaryItemData[0].trim();
      let secondaryPrice = parseFloat(secondaryItemData[1]);
      addItemToCart(secondaryName, secondaryPrice, 1); // Default quantity 1
    }
  });

  /* ============================  
       🛒 ADD ITEM TO CART FUNCTION  
       ============================ */
  function addItemToCart(name, price, quantity) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let newItem = { name, price, quantity };
    cart.push(newItem);
    localStorage.setItem("cart", JSON.stringify(cart));
  }
});
