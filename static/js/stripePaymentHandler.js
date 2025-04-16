// stripePaymentHandler.js

document.addEventListener("DOMContentLoaded", async function () {
  //  1. Initialize Stripe with your public key from Django
  const stripe = Stripe(window.stripePublicKey);

  //  2. Create Stripe Elements instance and mount card input
  const elements = stripe.elements();
  const card = elements.create("card");
  card.mount("#card-element");

  //  3. Get references to the payment form and error message area
  const form = document.getElementById("payment-form");
  const cardErrors = document.getElementById("card-errors");

  //  4. When the form is submitted
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    // ✅ Disable the submit button to prevent duplicate clicks
    const submitBtn = form.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";

    //  4a. Get selected order type (delivery or carryout)
    const orderType = document.querySelector('input[name="orderType"]:checked')?.value || "delivery";

    //  4b. Always get the email
    const email = document.getElementById("email")?.value;

    //  4c. If delivery, collect delivery fields
    const fullName = document.getElementById("fullName")?.value;
    const phone = document.getElementById("phone")?.value;
    const address = document.getElementById("address")?.value;
    const city = document.getElementById("city")?.value;
    const state = document.getElementById("state")?.value;
    const zip = document.getElementById("zip")?.value;
    const specialInstructions = document.getElementById("specialInstructions")?.value || "";

    //  5. Send all form data to Django to create a PaymentIntent
    const response = await fetch("/create-payment-intent/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        email,
        orderType,
        fullName,
        phone,
        address,
        city,
        state,
        zip,
        specialInstructions,
      }),
    });

    const result = await response.json();

    //  6. Handle server-side validation errors
    if (result.error) {
      cardErrors.textContent = result.error;
      submitBtn.disabled = false;
      submitBtn.textContent = "Pay Now";
      return;
    }

    const { clientSecret } = result;

    //  7. Confirm card payment using Stripe Elements
    const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: card,
        billing_details: {
          email: email,
        },
      },
    });

    //  8. Handle any card/payment errors from Stripe
    if (error) {
      cardErrors.textContent = error.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Pay Now";
    } else if (paymentIntent.status === "succeeded") {
      try {
        // ✅ Let backend store card info (via expanded charges)
        await fetch("/store-payment-details/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({
            paymentIntentId: paymentIntent.id,
          }),
        });
      } catch (err) {
        console.warn("Failed to store card details:", err);
      }

      //  9. Redirect to success page
      window.location.href = "/payment-success/";
    }
  });

  //  Utility function to get CSRF token from cookies
  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find((row) => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }
});
