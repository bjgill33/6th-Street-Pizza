document.addEventListener("DOMContentLoaded", function () {
  /* ===========================
       🛒 INITIALIZE CART FROM LOCAL STORAGE  
       =========================== */
  let cart = JSON.parse(localStorage.getItem("cart")) || []; // Load cart or initialize as empty

  function saveCart() {
    localStorage.setItem("cart", JSON.stringify(cart)); // ✅ Save cart to localStorage
    updateCartBadge(); // 🔥 Ensure badge updates when cart changes
  }

  /* ===========================
       🛒 ADD TO CART FUNCTION 
       =========================== */
  function addToCart() {
    // Extract item details from the order modal
    const itemName = document.getElementById("selectedItemName").textContent;
    const itemPrice = parseFloat(
      document.getElementById("orderModal").getAttribute("data-base-price")
    );
    const quantity = parseInt(document.getElementById("quantity").value);
    const size = document.getElementById("size").value;
    const toppings = Array.from(document.querySelectorAll(".topping:checked")).map((t) => t.value);

    // ✅ Find the original card by matching the item name
    let selectedCard = Array.from(document.querySelectorAll(".order-card")).find((card) =>
      card.querySelector(".menu_title")?.textContent.includes(itemName)
    );

    //  Extract category from the hidden input inside the selected card
    let category = "pizza"; // Default category
    if (selectedCard) {
      let hiddenCategoryInput = selectedCard.querySelector("input[type='hidden']");
      if (hiddenCategoryInput) {
        category = hiddenCategoryInput.value; // Get value from hidden input
      }
    }

    //  ICON MAPPING BASED ON CATEGORY
    const iconMap = {
      pizza: "cart_icons/pizza.png",
      chicken: "cart_icons/chicken.png",
      dessert: "cart_icons/ice-cream.png",
      drink: "cart_icons/drinks.png",
    };

    let categoryIcon = iconMap[category] || "cart_icons/pizza.png"; // Ensure fallback to pizza if undefined

    //  CALCULATE TOTAL ITEM PRICE
    let sizePrice = parseFloat(
      document.getElementById("size").options[document.getElementById("size").selectedIndex].dataset
        .price
    );
    let toppingsCost = toppings.length * 0.25;
    let totalItemPrice = (itemPrice + sizePrice + toppingsCost) * quantity;

    // CREATE CART ITEM OBJECT
    let cartItem = {
      name: itemName,
      size: size,
      quantity: quantity,
      toppings: toppings,
      price: totalItemPrice.toFixed(2),
      icon: categoryIcon,
    };

    //  ADD TO CART ARRAY & UPDATE DISPLAY
    cart.push(cartItem);
    saveCart(); // ✅ Persist cart data
    updateCartDisplay();
  }

  /* ===========================
       🛒 UPDATE CART DISPLAY 
       =========================== */
  function updateCartDisplay() {
    const cartContainer = document.querySelector(".cart-items-container");
    if (!cartContainer) return; // ✅ Prevent errors if cart display is missing

    // ✅ Ensure cart is always reloaded from localStorage before displaying
    cart = JSON.parse(localStorage.getItem("cart")) || [];

    cartContainer.innerHTML = "";
    let totalCartPrice = 0;
    let totalQuantity = 0;

    cart.forEach((item, index) => {
      totalCartPrice += parseFloat(item.price);
      totalQuantity += item.quantity;

      //  CREATE CART ITEM HTML WITH CATEGORY ICON
      const cartItemHTML = `
        <div class="d-flex align-items-center justify-content-between border-bottom py-2">
            <img src="${item.icon}" alt="${
        item.name
      }" style="width: 50px; height: 50px; object-fit: contain;">
            <div class="ms-2">
                <strong>${item.name} (${item.size})</strong><br>
                <small>Qty: ${item.quantity} | ${
        item.toppings.length ? "Toppings: " + item.toppings.join(", ") : "No extra toppings"
      }</small>
                <br><strong>Price: $${item.price}</strong>
            </div>
            <button class="btn btn-danger btn-sm" onclick="removeCartItem(${index})">
                <i class="bi bi-trash"></i>
            </button>
        </div>
      `;
      cartContainer.innerHTML += cartItemHTML;
    });

    //  UPDATE TOTAL PRICE DISPLAY
    let cartTotalElement = document.getElementById("cartTotal");
    if (cartTotalElement) {
      cartTotalElement.textContent = `$${totalCartPrice.toFixed(2)}`;
    }

    // ✅ UPDATE CART ICON BADGE ACROSS ALL PAGES
    updateCartBadge();
  }

  /* ===========================
       🎯 UPDATE CART BADGE  
       =========================== */
  function updateCartBadge() {
    let cartBadge = document.getElementById("cartBadge");
    if (!cartBadge) return; // Prevent errors if badge is missing

    let totalItems = cart.reduce((sum, item) => sum + item.quantity, 0); // Get total quantity
    cartBadge.textContent = totalItems;
  }

  /* ===========================
       🗑️ REMOVE ITEM FROM CART  
       =========================== */
  window.removeCartItem = function (index) {
    cart.splice(index, 1);
    saveCart();
    updateCartDisplay();
  };

  /* ===========================
       ❌ CLEAR CART FUNCTION
       =========================== */
  let clearCartBtn = document.getElementById("clearCart");
  if (clearCartBtn) {
    clearCartBtn.addEventListener("click", function () {
      cart = [];
      saveCart();
      updateCartDisplay();
    });
  }

  /* ===========================
       🔄 ENSURE CART DATA PERSISTS ACROSS PAGES
       =========================== */
  window.addEventListener("load", function () {
    cart = JSON.parse(localStorage.getItem("cart")) || [];
    updateCartDisplay();
  });

  /* ===========================
       🔄 SYNC CART BADGE ACROSS TABS  
       =========================== */
  window.addEventListener("storage", function () {
    cart = JSON.parse(localStorage.getItem("cart")) || [];
    updateCartBadge();
  });

  /* ===========================
       📌 ATTACH EVENT TO "ADD TO CART" BUTTON
       =========================== */
  let addToCartBtn = document.getElementById("addToCartBtn");
  if (addToCartBtn) {
    addToCartBtn.addEventListener("click", addToCart);
  }

  /* ===========================
       🔄 INITIAL CART DISPLAY ON PAGE LOAD  
       =========================== */
  updateCartDisplay();
});
