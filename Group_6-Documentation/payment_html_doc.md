# Payment.html Documentation
==========================

## Overview
------------

`payment.html` is the payment page of the 6th Street Pizza website. It contains the HTML structure and content for the payment process, including payment methods, order summary, and payment submission.

## Structure
-------------

The HTML document is divided into the following sections:

### Head

*   Contains metadata about the document, including the title, charset, and links to external stylesheets.

### Body

*   Contains the content of the HTML document, including the navbar, main content, and footer.

## Navbar
---------

The navbar is defined in the `<nav>` element and contains the following components:

### Brand

*   A link to the website's homepage, displayed as an image.

### Navigation Links

*   A list of links to other pages on the website, including the menu, locations, coupons, rewards, and tracker.

## Main Content
----------------

The main content of the page is contained within the `<div class="container">` element and includes:

### Payment Methods Section

*   A section that displays the available payment methods, including credit cards, PayPal, and cash.
*   Each payment method is represented by a radio button.

### Order Summary Section

*   A section that displays the order summary, including the order total, items, and subtotal.

### Payment Form

*   A form that collects payment information, including credit card number, expiration date, and security code.

### Submit Payment Button

*   A button that submits the payment information and completes the payment process.

## Payment Form Validation
-------------------------

The payment form is validated using JavaScript, which checks for the following:

### Credit Card Number

*   Must be a valid credit card number.

### Expiration Date

*   Must be a valid expiration date.

### Security Code

*   Must be a valid security code.

## Payment Submission
-------------------

When the payment is submitted, the following actions occur:

### Payment Processing

*   The payment information is sent to the payment gateway for processing.

### Order Confirmation

*   An order confirmation page is displayed, which includes the order details and a confirmation message.

## Scripts
------------

The document includes several scripts that provide functionality for the website, including:

### Bootstrap

*   A popular front-end framework that provides responsive design and UI components.

### Custom Scripts

*   Several custom scripts that provide functionality for the website, including payment form validation and payment submission.

## Functions
-------------

The document defines several functions that provide functionality for the website, including:

### validatePaymentForm()

*   A function that validates the payment form.

### submitPayment()

*   A function that submits the payment information and completes the payment process.

## Variables
-------------

The document defines several variables that store data used throughout the website, including:

### paymentMethods

*   An array of objects that store the payment method data, including the payment method name and icon.

### orderSummary

*   An object that stores the order summary data, including the order total, items, and subtotal.

# Specific Details

### Payment Methods

*   The available payment methods are displayed using radio buttons.
*   Each payment method is represented by a radio button with a corresponding label.
*   The user can select only one payment method at a time.

### Payment Form

*   The payment form includes the following fields:
    *   Credit Card Number: A text input field for the user to enter their credit card number.
    *   Expiration Date: A text input field for the user to enter the expiration date of their credit card.
    *   Security Code: A text input field for the user to enter the security code on the back of their credit card.
*   The payment form is validated using JavaScript to ensure that the credit card number, expiration date, and security code are valid.

### Payment Submission

*   When the user submits the payment form, the following actions occur:
    *   The payment information is sent to the payment gateway for processing.
    *   An order confirmation page is displayed, which includes the order details and a confirmation message.

### Payment Processing

*   The payment gateway processes the payment information and verifies it.
*   If the payment is successful, the order is processed and the user is redirected to the order confirmation page.
*   If the payment fails, an error message is displayed to the user and they are given the option to try again or cancel the payment.

### Order Confirmation

*   The order confirmation page includes the following information:
    *   Order Number: A unique identifier for the order.
    *   Order Date: The date the order was placed.
    *   Order Total: The total amount of the order.
    *   Order Items: A list of the items ordered, including the item name, quantity, and price.
    *   Confirmation Message: A message confirming that the payment was successful and the order has been processed.
