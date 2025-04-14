// stripePaymentHandler.js

document.addEventListener("DOMContentLoaded", async function () {
  // Initialize Stripe with the public key injected by Django
  const stripe = Stripe(window.stripePublicKey);

  // Create Stripe Elements instance
  const elements = stripe.elements();

  // Create a card input and mount it
  const card = elements.create("card");
  card.mount("#card-element");

  // Reference to the form and the error container
  const form = document.getElementById("payment-form");
  const cardErrors = document.getElementById("card-errors");

  // Handle form submission
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;

    // Send request to Django to create a payment intent
    const response = await fetch("/create-payment-intent/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ email: email }),
    });

    const result = await response.json();

    if (result.error) {
      cardErrors.textContent = result.error;
      return;
    }

    const { clientSecret } = result;

    // Use Stripe to confirm the payment
    const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: card,
        billing_details: {
          email: email,
        },
      },
    });

    if (error) {
      // Handle Stripe error (e.g., declined card)
      cardErrors.textContent = error.message;
    } else if (paymentIntent.status === "succeeded") {
      // Redirect to success page
      window.location.href = "/payment-success/";
    }
  });

  // Utility function to get CSRF token from cookie
  function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }
});
