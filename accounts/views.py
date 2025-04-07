# Import Stripe's official Python library
import stripe

# Import Django settings to access the Stripe secret key from settings.py
from django.conf import settings

# Import Django's email sending function (can be swapped for SendGrid)
from sendgrid import SendGridAPIClient  # or SendGrid
from sendgrid.helpers.mail import Mail

# Allow this view to be accessed without CSRF protection (useful for APIs)
from django.views.decorators.csrf import csrf_exempt

# Used to return JSON responses (like Stripe session ID)
from django.http import JsonResponse

# Import Django utilities for rendering templates and handling HTTP responses
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

# Import models for pizzas, wings, drinks, desserts, and toppings
from accounts.models import Pizza, Wing, Drink, Dessert, Topping

# Set up logging to track errors or warnings in the application
import logging

# Import JSON encoder to serialize Python objects for frontend consumption
from django.core.serializers.json import DjangoJSONEncoder
import json

# Import Decimal to ensure proper handling of currency and numeric precision
from decimal import Decimal

# Create a logger to log warnings and errors
logger = logging.getLogger(__name__)

# Set the Stripe secret API key from Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# Set the Stripe secret API key from Django settings
sg_api_key = settings.SEND_GRID_API_KEY


# Helper function to retrieve an object safely or log a warning if not found
def safe_get(model, name):
    item = model.objects.filter(name=name).first()
    if not item:
        logger.warning(f"{model.__name__} with name '{name}' not found.")
    return item


# Render the homepage with menu items and toppings. Toppings are passed as JSON
def home(request):
    # Retrieve all toppings and serialize them for the frontend
    toppings_qs = Topping.objects.all()
    toppings_data = list(toppings_qs.values("name", "price"))

    # Define the context for the homepage with pizzas, wings, drinks, and desserts
    context = {
        # Pizzas
        "cheese": Pizza.objects.get(id=13),
        "veggie": Pizza.objects.get(id=14),
        "pepperoni": Pizza.objects.get(id=15),
        "margherita": Pizza.objects.get(id=17),
        "meatlovers": Pizza.objects.get(id=19),

        # Wings
        "buffalo": Wing.objects.get(id=2),
        "bbq_wings": Wing.objects.get(id=3),
        "hothoney": Wing.objects.get(id=4),
        "drpepper": Wing.objects.get(id=5),

        # Drinks
        "coke": Drink.objects.get(id=2),
        "rootbeer": Drink.objects.get(id=3),
        "water": Drink.objects.get(id=4),

        # Desserts
        "lava_cake": Dessert.objects.get(id=1),
        "chocolate_chip_cookies": Dessert.objects.get(id=2),
        "milkshake": Dessert.objects.get(id=3),

        # Toppings passed as JSON
        "toppings_json": json.dumps(toppings_data, cls=DjangoJSONEncoder),
    }
    return render(request, "index.html", context)


# Render the menu page
def menu(request):
    # Retrieve all toppings and serialize them for the frontend menu page
    toppings_qs = Topping.objects.all()
    toppings_data = list(toppings_qs.values("name", "price"))

    # Define the context for the menu page with pizzas, wings, drinks, and desserts
    context = {
        # Pizzas
        "cheese": Pizza.objects.get(id=13),
        "veggie": Pizza.objects.get(id=14),
        "pepperoni": Pizza.objects.get(id=15),
        "margherita": Pizza.objects.get(id=17),
        "meatlovers": Pizza.objects.get(id=19),

        # Wings
        "buffalo": Wing.objects.get(id=2),
        "bbq_wings": Wing.objects.get(id=3),
        "hothoney": Wing.objects.get(id=4),
        "drpepper": Wing.objects.get(id=5),

        # Drinks
        "coke": Drink.objects.get(id=2),
        "rootbeer": Drink.objects.get(id=3),
        "water": Drink.objects.get(id=4),

        # Desserts
        "lava_cake": Dessert.objects.get(id=1),
        "chocolate_chip_cookies": Dessert.objects.get(id=2),
        "cheese_cake": Dessert.objects.get(id=3),

        # Toppings passed as JSON
        "toppings_json": json.dumps(toppings_data, cls=DjangoJSONEncoder),
    }
    return render(request, "menu.html", context)


# Render the payment page
def payment(request):
    return render(request, 'payment.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


# Sends email to user when payment is successful
@csrf_exempt
def payment_success(request):
    # Retrieve delivery and cart data from session
    cart = request.session.get('cart', {})

    sg = SendGridAPIClient(sg_api_key)
    
    # Retrieve metadata sent via Stripe 
    customer_email = request.session.get("customer_email", "customer@example.com")

    # Build order summary
    order_lines = []
    total_price = 0
    for item in cart.values():
        line = f"{item['quantity']}x {item['name']} ({item.get('size', '')})"
        if item.get('toppings'):
            line += f" - Toppings: {', '.join(item['toppings'])}"
        item_total = float(item['price']) * item['quantity']
        total_price += item_total
        line += f" - ${item_total:.2f}"
        order_lines.append(line)

    order_summary = "\n".join(order_lines)
    total_formatted = f"${total_price:.2f}"

    # Sending confirmation email
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=customer_email,
        subject="Your 6th Street Pizza Order Confirmation",
        plain_text_content=f"Thank you for your order! 🍕"
    )

    try:
        sg.send(message)
    except Exception as e:
        print("SendGrid error:", e)

    # Clear the cart from session
    request.session['cart'] = {}

    # Render payment_success
    return render(request, "payment_success.html", {
        "total": total_formatted,
        "items": order_lines
    })


# Retrieve the cart from the session or return an empty cart if it does not exist
def get_cart(request):
    """Retrieve the cart from the session"""
    return request.session.get('cart', {})


# Save the updated cart to the session and mark the session as modified
def save_cart(request, cart):
    """Save the cart to the session"""
    request.session['cart'] = cart
    request.session.modified = True


# Add an item to the cart. This handles adding pizzas, wings, drinks, and desserts
def add_to_cart(request):
    if request.method == "POST":
        try:
            # Retrieve data from the request
            product_id = request.POST.get("product_id")
            category = request.POST.get("category")
            # Default to medium for pizzas
            size = request.POST.get("size", "medium")
            # Default to 1 if no quantity provided
            quantity = int(request.POST.get("quantity", 1))
            # Get toppings JSON or default to empty list
            toppings_raw = request.POST.get("toppings_json", "[]") or "[]"
            toppings_json = json.loads(toppings_raw)

            # Load the current cart from the session
            cart = get_cart(request)

            product = None
            price = 0
            toppings_price = 0

            # Check the category and retrieve the corresponding product and price
            if category == "pizza":
                product = get_object_or_404(Pizza, id=product_id)
                price = Decimal(
                    str(getattr(product, f"price_{size}", product.price_medium)))

                # Calculate the price of selected toppings
                if toppings_json:
                    toppings = Topping.objects.filter(name__in=toppings_json)
                    toppings_price = sum(Decimal(str(topping.price))
                                         for topping in toppings)
            elif category == "wing":
                product = get_object_or_404(Wing, id=product_id)
                price = Decimal(str(product.price))
            elif category == "drink":
                product = get_object_or_404(Drink, id=product_id)
                price = Decimal(str(product.price))
            elif category == "dessert":
                product = get_object_or_404(Dessert, id=product_id)
                price = Decimal(str(product.price))
            else:
                # Return error if category is invalid
                return JsonResponse({"error": "Invalid category"}, status=400)

            # Calculate the total price including toppings
            total_price = price + Decimal(str(toppings_price))

            # Create a unique key for the item, including size for pizzas
            product_key = f"{category}_{product_id}_{size}" if category == "pizza" else f"{category}_{product_id}"

            # Check if the item already exists in the cart
            if product_key in cart:
                cart[product_key]['quantity'] += quantity
            else:
                # Add a new item to the cart
                cart[product_key] = {
                    'name': product.name,
                    # Store as a string to avoid JSON serialization issues
                    'price': str(total_price),
                    'quantity': quantity,
                    'category': category,
                    'size': size if category == "pizza" else None,
                    'toppings': toppings_json if category == "pizza" else [],
                    'toppings_price': str(toppings_price),
                }

            # Save the updated cart to the session
            save_cart(request, cart)

            # Return a success response with the updated cart
            return JsonResponse({"message": "added", "cart": cart})

        except Exception as e:
            # Return error response if there is any exception
            return JsonResponse({"error": str(e)}, status=500)

    # Return an error if the request method is not POST
    return JsonResponse({"error": "invalid method"}, status=400)


# Remove an item from the cart based on its unique key
def remove_from_cart(request):
    """Remove an item from the cart"""
    if request.method == "POST":
        product_key = request.POST.get('product_key')
        cart = get_cart(request)

        # Check if the item is in the cart and remove it
        if product_key in cart:
            del cart[product_key]
            save_cart(request, cart)

        return JsonResponse({'message': 'Item removed from cart', 'cart': cart})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Update the quantity of an item in the cart
def update_cart(request):
    """Update an item quantity in the cart and recalculate totals"""
    if request.method == "POST":
        try:
            # Load JSON data sent from fetch() in cartHandler.js
            data = json.loads(request.body)
            product_key = data.get('product_key')
            quantity = int(data.get('quantity', 1))

            # Get and modify the cart
            cart = get_cart(request)

            # Update quantity if the item is in the cart
            if product_key in cart:
                if quantity > 0:
                    cart[product_key]['quantity'] = quantity
                else:
                    # Remove item if quantity is set to 0
                    del cart[product_key]

                # Save updated cart to session
                save_cart(request, cart)

                # ✅ Calculate and add updated item subtotals and total price
                cart_with_totals = calculate_cart_totals(cart)

                # Return updated cart data with new totals
                return JsonResponse({'message': 'Cart updated', 'cart': cart_with_totals})

            return JsonResponse({'error': 'Invalid product key'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Helper function to calculate item subtotals and cart total
def calculate_cart_totals(cart):
    """Calculate item subtotals and total for the updated cart"""
    total_price = 0

    for key, item in cart.items():
        price = float(item.get('price', 0))
        quantity = int(item.get('quantity', 0))
        subtotal = price * quantity
        item['subtotal'] = round(subtotal, 2)
        total_price += subtotal

    return {'items': cart, 'total_price': round(total_price, 2)}


# Return the current cart data in JSON format for the frontend
def get_cart_data(request):
    cart = get_cart(request)
    print("Cart session:", cart)  # Log the current cart for debugging purposes
    return JsonResponse({'cart': cart})


# Render the cart page with the current cart data
def cart_view(request):
    """Render cart page"""
    cart = get_cart(request)
    return render(request, 'cart.html', {'cart': cart})


# Clear all items in the cart and redirect the user to the menu page
def clear_cart(request):
    request.session['cart'] = {}  # Clear the cart in session
    return redirect('menu')



@csrf_exempt
def create_payment_intent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            request.session["customer_email"] = email

            cart = request.session.get("cart", {})
            if not cart:
                return JsonResponse({"error": "Cart is empty"}, status=400)

            total = sum(float(item["price"]) * item["quantity"] for item in cart.values())
            amount_in_cents = int(total * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",
                receipt_email=email,
                metadata={"integration_check": "accept_a_payment"},
            )

            return JsonResponse({"clientSecret": intent.client_secret})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

