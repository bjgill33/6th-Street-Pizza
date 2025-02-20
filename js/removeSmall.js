// Arthur Holmes
// 2/18/2025
// ============================================
// 🛒 REMOVE "(small)" FROM NON-PIZZA ITEMS IN CART
// ============================================
//
// This script ensures that the word "(small)" does not appear for non-pizza
// items in the shopping cart. Since "small" is the default size for pizzas,
// it was incorrectly being applied to all items in the cart, including drinks
// and desserts. To fix this, the script performs the following actions:
//
//  Listens for a click on the .bi-cart icon before running (prevents unnecessary execution).
//  Finds all <strong> tags inside the cart, where item names are displayed.
//  Checks if the item name contains the word "pizza." If not, it removes "(small)".
//  Uses regular expressions to dynamically replace "(small)" only when necessary.
//  Runs only when the cart button is clicked, ensuring efficiency.
//
// This approach prevents incorrect size labels on non-pizza items while
// keeping the cart display accurate.

document.addEventListener("DOMContentLoaded", function () {
  // Select the cart button (bi-cart icon)
  const cartButton = document.querySelector(".bi-cart");

  // Function to remove "(small)" from non-pizza items
  function removeSmallFromNonPizzaItems() {
    // Select all strong tags inside cart items
    const cartItems = document.querySelectorAll(".cart-items-container strong");

    cartItems.forEach((item) => {
      let itemText = item.textContent.toLowerCase(); // Convert text to lowercase for matching

      // ✅ If "pizza" is NOT found, remove "(small)"
      if (!itemText.includes("pizza")) {
        item.textContent = item.textContent.replace(/\(small\)/gi, "").trim(); // Removes "(small)"
      }
    });
  }

  // ✅ Run the function when the cart button is clicked
  cartButton.addEventListener("click", removeSmallFromNonPizzaItems);
});
