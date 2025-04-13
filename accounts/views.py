# --------------------------------------------
#  Django Framework Utilities
# --------------------------------------------

# Used to render HTML templates and fetch DB objects safely
from django.shortcuts import render, get_object_or_404

# Allows returning JSON responses (e.g., for AJAX calls)
from django.http import JsonResponse

# Enables cross-site request forgery exemption (for POST APIs like Stripe)
from django.views.decorators.csrf import csrf_exempt

# Used to show messages to the user (e.g., "Order submitted successfully")
from django.contrib import messages

# Provides access to global project settings (Stripe key, email, etc.)
from django.conf import settings

# --------------------------------------------
#  Database Models
# --------------------------------------------

# Models for food items and restaurant locations
from accounts.models import Pizza, Wing, Drink, Dessert, Topping
from .models import RestaurantLocation

# --------------------------------------------
#  Logging & Data Handling
# --------------------------------------------

# Enables application logging for debugging or error tracking
import logging

# Used to safely encode complex data types (like Decimal) to JSON
from django.core.serializers.json import DjangoJSONEncoder

# Handles general-purpose JSON parsing/handling
import json

# Handles currency math precisely without floating point issues
from decimal import Decimal

# Initialize logger for this file/module
logger = logging.getLogger(__name__)

# --------------------------------------------
#  SendGrid Email Service
# --------------------------------------------

# Used to send transactional emails (order confirmation)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --------------------------------------------
#  Stripe Payment Integration
# --------------------------------------------

# Stripe Python SDK to handle payments securely
import stripe

# Set Stripe's secret key from your Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY



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
from .models import RestaurantLocation


def get_all_toppings():
    toppings_qs = Topping.objects.all()
    return [
        {
            "name": topping.name,
            "price": float(topping.price)  # convert Decimal to float
        }
        for topping in toppings_qs
    ]


def payment(request):
    location_key = request.session.get("selected_location")
    store_info = None
    print("Store Location in Session:", location_key)

    if location_key:
        store_number = location_key.replace("store", "")
        try:
            store_info = RestaurantLocation.objects.get(store_number=store_number)
        except RestaurantLocation.DoesNotExist:
            store_info = None

    if not store_info:
        messages.error(request, "No location selected. Please go back and choose a store.")
        return redirect("home")

    context = {
        "store_info": store_info,
        "toppings_json": json.dumps(get_all_toppings(), default=str),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY
    }

    return render(request, "payment.html", context)


# create_payment_intent

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


# Within this is some code for trying to set up SendGrid

@csrf_exempt
def payment_success(request):
    # Retrieve delivery and cart data from session
    cart = request.session.get('cart', {})

    sg = SendGridAPIClient(settings.SEND_GRID_API_KEY)

    # Retrieve metadata sent via Stripe
    customer_email = request.session.get("customer_email", "customer@example.com")

    # order summary
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

    # Retrieve store info from session
    location_key = request.session.get("selected_location")
    store_info = None
    if location_key:
        store_number = location_key.replace("store", "")
        store_info = RestaurantLocation.objects.filter(store_number=store_number).first()

    # Clear the cart from session
    request.session['cart'] = {}

    # Render payment_success with order and location info
    return render(request, "payment_success.html", {
        "total": total_formatted,
        "items": order_lines,
        "store_info": store_info,
    })


# set location for pickup and delivery
@csrf_exempt
def set_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location = data.get('location')
            if location in ['store1', 'store2', 'store3']:
                request.session['selected_location'] = location
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'error': 'Invalid location'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Retrieve store info
def get_locations(request):
    locations = RestaurantLocation.objects.filter(status="Open")
    data = []
    for loc in locations:
        data.append({
            "id": loc.id,
            "store_number": loc.store_number,
            "address": loc.address,
            "city": loc.city,
            "state": loc.state,
            "zip": loc.zip_code,
            "phone": loc.phone
        })
    return JsonResponse({"locations": data})


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
            size = request.POST.get("size", "medium")  # Default to medium for pizzas
            quantity = int(request.POST.get("quantity", 1))  # Default to 1 if no quantity provided
            toppings_raw = request.POST.get("toppings_json", "[]") or "[]"  # Get toppings JSON or default to empty list
            toppings_json = json.loads(toppings_raw)

            # Load the current cart from the session
            cart = get_cart(request)

            product = None
            price = 0
            toppings_price = 0

            # Check the category and retrieve the corresponding product and price
            if category == "pizza":
                product = get_object_or_404(Pizza, id=product_id)
                price = Decimal(str(getattr(product, f"price_{size}", product.price_medium)))

                # Calculate the price of selected toppings
                if toppings_json:
                    toppings = Topping.objects.filter(name__in=toppings_json)
                    toppings_price = sum(Decimal(str(topping.price)) for topping in toppings)
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
                    'price': str(total_price),  # Store as a string to avoid JSON serialization issues
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
                    del cart[product_key]  # Remove item if quantity is set to 0

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
