// orderTypeHandler.js
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("payment-form");

  if (!form) return;

  form.addEventListener("submit", function (event) {
    // Remove old input if it exists to avoid duplicates
    const oldInput = document.querySelector("#orderTypeHiddenInput");
    if (oldInput) oldInput.remove();

    // Get the selected radio value
    const selectedOrderType = document.querySelector('input[name="orderType"]:checked')?.value || "delivery";

    // Inject hidden input into the form
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "orderType";
    hiddenInput.id = "orderTypeHiddenInput";
    hiddenInput.value = selectedOrderType;

    form.appendChild(hiddenInput);
  });
});
