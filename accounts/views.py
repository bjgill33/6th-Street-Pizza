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
from accounts.models import OrderPizza, OrderWings, OrderDrinks, OrderDesserts

from .models import RestaurantLocation
from .models import Order
from .models import DiscountCode

# --------------------------------------------
#  Logging & Data Handling
# --------------------------------------------

# Enables application logging for debugging or error tracking
import logging

# Used to safely encode complex data types (like Decimal) to JSON
from django.core.serializers.json import DjangoJSONEncoder

# Handles general-purpose JSON parsing/handling
import json


# For regular expression
import re

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
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

# --------------------------------------------
#  Stripe Payment Integration
# --------------------------------------------

# Stripe Python SDK to handle payments securely
import stripe

# Django Framework Utilities
from django.shortcuts import render, get_object_or_404, redirect

# Decorator to restrict a Django view to accept only HTTP POST requests for security and proper usage
from django.views.decorators.http import require_POST

# Set Stripe's secret key from your Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY


# Allows this view to bypass Django's default CSRF protection (because it's being called via AJAX)
@csrf_exempt
# Ensures that only HTTP POST requests are allowed for this view
@require_POST
def save_delivery_info(request):
    """
    View to capture delivery information submitted from the homepage modal
    and store it into the Django session for later use (e.g., pre-populating the payment page).
    """
    try:
        # Parse JSON data sent from the frontend
        data = json.loads(request.body)

        # Save delivery details into the Django session
        request.session["full_name"] = data.get("fullName")
        request.session["email"] = data.get("email")
        request.session["phone"] = data.get("phone")
        request.session["address"] = data.get("address")
        request.session["city"] = data.get("city")
        request.session["state"] = data.get("state")
        request.session["zip"] = data.get("zip")
        request.session["special_instructions"] = data.get("specialInstructions")

        # Mark the session as modified to ensure Django saves the changes
        request.session.modified = True

        # Return success response
        return JsonResponse({"status": "success"})

    except Exception as e:
        # Return an error response if anything goes wrong
        return JsonResponse({"error": str(e)}, status=400)


def apply_coupon(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"valid": False, "error": "No code provided"})

    try:
        coupon = DiscountCode.objects.get(code__iexact=code, is_active=True)
        request.session["applied_discount"] = {
            "name": coupon.name,
            "percentage": coupon.percentage,
            "code": coupon.code,
        }
        return JsonResponse({
            "valid": True,
            "name": coupon.name,
            "percentage": coupon.percentage,
        })
    except DiscountCode.DoesNotExist:
        return JsonResponse({"valid": False, "error": "Invalid or expired coupon"})


# Render the Locations page
def locations_page(request):
    location_key = request.session.get("selected_location")
    store_info = None

    if location_key:
        store_number = location_key.replace("store", "")
        store_info = RestaurantLocation.objects.filter(store_number=store_number).first()

    stores = RestaurantLocation.objects.filter(status="Open")

    # Attach placeholder images instead of embed codes
    for store in stores:
        if store.store_number == "1":
            store.embed_code = '<img src="https://placehold.co/600x200?text=Store+1+Map" class="w-100" height="200" alt="Store 1 Map Placeholder">'
        elif store.store_number == "2":
            store.embed_code = '<img src="https://placehold.co/600x200?text=Store+2+Map" class="w-100" height="200" alt="Store 2 Map Placeholder">'
        elif store.store_number == "3":
            store.embed_code = '<img src="https://placehold.co/600x200?text=Store+3+Map" class="w-100" height="200" alt="Store 3 Map Placeholder">'

    return render(request, "store_locations.html", {
        "store_info": store_info,
        "stores": stores,
        "applied_discount": request.session.get("applied_discount"),
    })


# Render the Coupons page
def coupons_page(request):
    # Only show active discount codes
    discounts = DiscountCode.objects.filter(is_active=True)

    # Optional: pull applied discount from session
    applied_discount = request.session.get("applied_discount")

    return render(request, "coupons.html", {
        "discounts": discounts,
        "applied_discount": applied_discount,
    })


# update the coupon validation view to store the coupon in session:
def validate_coupon(request):
    code = request.GET.get('code', '').strip()
    cart = request.session.get('cart', {})

    try:
        discount = DiscountCode.objects.get(code__iexact=code, is_active=True)

        # Only one discount per cart/session
        request.session['applied_discount'] = {
            "name": discount.name,
            "code": discount.code,
            "percentage": float(discount.percentage),  # Convert Decimal to float
        }

        return JsonResponse({
            "valid": True,
            "name": discount.name,
            "code": discount.code,
            "percentage": float(discount.percentage),  # Convert Decimal to float
        })

    except DiscountCode.DoesNotExist:
        return JsonResponse({"valid": False, "error": "Invalid or expired discount code."})


# clear coupon
def clear_coupon(request):
    if 'applied_discount' in request.session:
        del request.session['applied_discount']
    return JsonResponse({'cleared': True})


# -------------------------------------------------------------
# Helper: Convert structured order data into readable summary
# -------------------------------------------------------------
def render_order_summary(order_data):
    items = []  # This will hold each item line for the final summary

    # -----------------------------
    # Pizzas Section
    # -----------------------------
    for pizza in order_data.get("pizzas", []):
        # Format toppings if they exist
        topping_str = (
            f" - Toppings: {', '.join(pizza.get('toppings', []))}"
            if pizza.get("toppings") else ""
        )
        # Example: 2x Pepperoni Pizza (Large) - Toppings: Mushrooms, Olives
        items.append(
            f"{pizza['quantity']}x {pizza['name']} ({pizza['size'].capitalize()}){topping_str}"
        )

    # -----------------------------
    # Wings Section
    # -----------------------------
    for wing in order_data.get("wings", []):
        # Example: 1x 6 Buffalo Chicken Wings
        items.append(f"{wing['quantity']}x {wing['flavor']}")

    # -----------------------------
    # Drinks Section
    # -----------------------------
    for drink in order_data.get("drinks", []):
        # Example: 1x 2 Liter Coca-Cola
        items.append(f"{drink['quantity']}x {drink['name']}")

    # -----------------------------
    # Desserts Section
    # -----------------------------
    for dessert in order_data.get("desserts", []):
        # Example: 2x Cheesecake
        items.append(f"{dessert['quantity']}x {dessert['name']}")

    # Return all items joined with line breaks
    return "\n".join(items)


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


def get_all_toppings():
    toppings_qs = Topping.objects.all()
    return [
        {
            "name": topping.name,
            "price": float(topping.price)  # convert Decimal to float
        }
        for topping in toppings_qs
    ]


# Payment solution
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
        # If no valid store, try assigning a default store (Store 1)
        default_store = RestaurantLocation.objects.filter(store_number="1").first()
        if default_store:
            request.session["selected_location"] = "store1"
            request.session.modified = True
            store_info = default_store
        else:
            messages.error(request, "No location selected. Please go back and choose a store.")
            return redirect("home")

    context = {
        "store_info": store_info,
        "toppings_json": json.dumps(get_all_toppings(), default=str),
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "applied_discount": request.session.get("applied_discount"),  # Keep discount working too
    }

    return render(request, "payment.html", context)


# Track the order

# -------------------------------------------------------
# View: Track an order using the tracking_id from URL
# -------------------------------------------------------
def track_order(request):
    # -------------------------------
    # Get tracking ID from the request
    # -------------------------------
    tracking_id = request.GET.get('tracking_id')

    # -------------------------------
    # Default context to render the page
    # -------------------------------
    context = {
        "tracking_attempted": True,  # Used to hide/show results in the template
        "order_found": False,  # Flag to control display of order info
        "tracking_id": tracking_id,  # Echo back the entered ID
        "applied_discount": request.session.get("applied_discount"),
    }

    # -------------------------------
    # If a tracking ID was submitted
    # -------------------------------
    if tracking_id:
        # Try to find the order in the database
        order = Order.objects.filter(tracking_id=tracking_id).select_related('restaurant_location').first()

        # -------------------------------
        # If order is found, populate context
        # -------------------------------
        if order:
            store = order.restaurant_location  # Store that fulfilled the order

            # Parse JSON string from order_summary field
            order_summary_data = json.loads(order.order_summary) if order.order_summary else {}

            # Extract and format items ordered using helper
            parsed_items = render_order_summary(order_summary_data.get("order", {}))

            # Get total paid from summary (fallback to model field if missing)
            total_paid = order_summary_data.get("total_price", order.total_price)

            # Update context with all order details
            context.update({
                "order_found": True,
                "order": order,
                "store": store,
                "order_type": order.delivery_method.lower(),
                "status": "Order Received",  # we can later pull this from DB or enum
                "progress_percent": 75,  # update later
                "order_summary_parsed": parsed_items,
                "total": f"${total_paid:.2f}" if total_paid else "$0.00"
            })

    # -------------------------------
    # Render the tracking page
    # -------------------------------
    return render(request, "tracking.html", context)


# create_payment_intent

@csrf_exempt
def create_payment_intent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Store email and order type
            email = data.get("email")
            order_type = data.get("orderType", "delivery").lower()
            request.session["customer_email"] = email
            request.session["order_type"] = order_type

            # Save delivery info if applicable
            if order_type == "delivery":
                request.session["full_name"] = data.get("fullName")
                request.session["phone"] = data.get("phone")
                request.session["address"] = data.get("address")
                request.session["city"] = data.get("city")
                request.session["state"] = data.get("state")
                request.session["zip"] = data.get("zip")
                request.session["special_instructions"] = data.get("specialInstructions")

            # Retrieve cart from session
            cart = request.session.get("cart", {})
            if not cart:
                return JsonResponse({"error": "Cart is empty"}, status=400)

            # Calculate subtotal
            subtotal = sum(float(item["price"]) * item["quantity"] for item in cart.values())

            # Apply discount only for carryout or pickup
            applied_discount = request.session.get("applied_discount") if order_type in ["pickup", "carryout"] else None
            discount_amount = 0.0
            if applied_discount:
                discount_percentage = float(applied_discount.get("percentage", 0))
                discount_amount = round(subtotal * discount_percentage / 100, 2)

            # Compute tax and final total
            tax_rate = 0.0725  # 7.25%
            subtotal_after_discount = round(subtotal - discount_amount, 2)
            sales_tax = round(subtotal_after_discount * tax_rate, 2)
            final_total = round(subtotal_after_discount + sales_tax, 2)

            # Save calculations to session
            request.session["calculated_subtotal"] = round(subtotal, 2)
            request.session["calculated_discount"] = discount_amount
            request.session["calculated_tax"] = sales_tax
            request.session["calculated_total"] = final_total

            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(final_total * 100),  # cents
                currency="usd",
                receipt_email=email,
                metadata={"integration_check": "accept_a_payment"},
            )

            return JsonResponse({
                "clientSecret": intent.client_secret,
                "finalTotal": int(final_total * 100)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# Payment Display
@csrf_exempt
def payment_success(request):
    # Step 1: Retrieve cart and determine delivery method
    cart = request.session.get('cart', {})
    order_type_raw = request.session.get("order_type", "delivery").lower()
    order_type_map = {"pickup": "Pickup", "carryout": "Pickup", "delivery": "Delivery"}
    delivery_method = order_type_map.get(order_type_raw, "Pickup")
    state_abbr = "NC"

    # Step 2: Retrieve and sanitize user fields
    def sanitize(value, max_length):
        if isinstance(value, str):
            value = re.sub(r"[<>;'\\]", "", value.strip())
            return value[:max_length]
        return value

    full_name = sanitize(request.session.get("full_name", "Guest"), 50)
    phone = sanitize(request.session.get("phone", "N/A"), 15)
    customer_email = sanitize(request.session.get("customer_email", "customer@example.com"), 80)
    special_instructions = sanitize(request.session.get("special_instructions", ""), 100)

    # Step 3: Get selected store info
    location_key = request.session.get("selected_location")
    store_info = None
    if location_key:
        store_number = location_key.replace("store", "")
        store_info = RestaurantLocation.objects.filter(store_number=store_number).first()

    # Step 4: Retrieve delivery or store address
    if delivery_method.lower() == "delivery":
        address = sanitize(request.session.get("address", ""), 100)
        city = sanitize(request.session.get("city", ""), 50)
        zip_code = sanitize(request.session.get("zip", ""), 5)
    else:
        address = store_info.address if store_info else "N/A"
        city = store_info.city if store_info else "N/A"
        zip_code = store_info.zip_code if store_info else "00000"

    # Step 5: Build order summary lines
    order_lines = []
    for item in cart.values():
        line = f"{item['quantity']}x {item['name']} ({item.get('size', '')})"
        if item.get('toppings'):
            line += f" - Toppings: {', '.join(item['toppings'])}"
        item_total = float(item['price']) * item['quantity']
        line += f" - ${item_total:.2f}"
        order_lines.append(line)

    # Step 6: Load calculated values from session (no recalculation)
    estimated_subtotal = float(request.session.get("calculated_subtotal", 0))
    discount_amount = float(request.session.get("calculated_discount", 0))
    sales_tax = float(request.session.get("calculated_tax", 0))
    estimated_total = float(request.session.get("calculated_total", 0))
    applied_discount = request.session.get('applied_discount') if order_type_raw in ["pickup", "carryout"] else None

    # grab discount code to be placed in the order view
    discount_percentage = None
    if applied_discount and applied_discount.get("code"):
        try:
            discount_obj = DiscountCode.objects.get(code=applied_discount["code"])
            discount_percentage = discount_obj.percentage
        except DiscountCode.DoesNotExist:
            discount_percentage = None

    # Step 7: Create initial order record
    order = Order.objects.create(
        name=full_name,
        phone=phone,
        address=address,
        city=city,
        state=state_abbr,
        zip_code=zip_code,
        email=customer_email,
        delivery_method=delivery_method,
        special_instructions=special_instructions,
        total_price=estimated_total,
        subtotal_before_discount=estimated_subtotal,
        discount_amount=discount_amount,
        sales_tax=sales_tax,
        coupon=applied_discount.get("code") if applied_discount else None,
        card_last_four=request.session.get("card_last4"),
        card_expiry_date=request.session.get("card_expiry"),
        card_type=request.session.get("card_type") or "Unknown",
        restaurant_location=store_info,
        payment_confirmation="Paid"
    )
    # Match the order with the
    order_summary = {
        "email": customer_email,
        "name": full_name,
        "phone": phone,
        "address": {
            "street": address,
            "city": city,
            "zipcode": zip_code,
            "state": state_abbr
        },
        "store_location": {
            "store_number": store_info.store_number if store_info else None,
            "address": {
                "street": store_info.address if store_info else "",
                "city": store_info.city if store_info else "",
                "state": store_info.state if store_info else ""
            }
        },
        "special_instructions": special_instructions or "None",
        "tracking_id": order.tracking_id,
        "subtotal_before_discount": estimated_subtotal, "discount_amount": discount_amount,
        "sales_tax": sales_tax,
        "tax_rate": 0.0725,
        "coupon": applied_discount.get("code") if applied_discount else None,
        "discount_percentage": discount_percentage,
        "total_price": estimated_subtotal - discount_amount + sales_tax,

    }

    if applied_discount:
        order._applied_discount = applied_discount

    # Step 8: Save order items by category
    for key, item in cart.items():
        category = item.get("category")
        quantity = item.get("quantity", 1)

        if category == "pizza":
            pizza = Pizza.objects.filter(id=int(key.split("_")[1])).first()
            toppings = item.get("toppings", [])
            topping_objs = Topping.objects.filter(name__in=toppings)
            OrderPizza.objects.create(
                order=order,
                pizza=pizza,
                size=item.get("size", "medium"),
                quantity=quantity,
                topping_1=topping_objs[0] if len(topping_objs) > 0 else None,
                topping_2=topping_objs[1] if len(topping_objs) > 1 else None,
                topping_3=topping_objs[2] if len(topping_objs) > 2 else None
            )

        elif category == "wing":
            wing = Wing.objects.filter(id=int(key.split("_")[1])).first()
            OrderWings.objects.create(order=order, wing=wing, quantity=quantity)

        elif category == "drink":
            drink = Drink.objects.filter(id=int(key.split("_")[1])).first()
            OrderDrinks.objects.create(order=order, drink=drink, quantity=quantity)

        elif category == "dessert":
            dessert = Dessert.objects.filter(id=int(key.split("_")[1])).first()
            OrderDesserts.objects.create(order=order, dessert=dessert, quantity=quantity)

    order.order_summary = json.dumps(order_summary, default=str)
    order.save()

    # Step 9: Build HTML and plain text email
    delivery_details_html = ""
    delivery_details_text = ""
    if delivery_method.lower() == "delivery":
        delivery_details_html = f"""
        <h3 style='color:#BB2D3B;'>Delivery Details:</h3>
        <table style='width:100%;background:#F8F9FA;'>
            <tr><td><strong>Name:</strong></td><td>{full_name}</td></tr>
            <tr><td><strong>Phone:</strong></td><td>{phone}</td></tr>
            <tr><td><strong>Street:</strong></td><td>{address}</td></tr>
            <tr><td><strong>City:</strong></td><td>{city}</td></tr>
            <tr><td><strong>State:</strong></td><td>{state_abbr}</td></tr>
            <tr><td><strong>Zip:</strong></td><td>{zip_code}</td></tr>
            <tr><td><strong>Instructions:</strong></td><td>{special_instructions or 'N/A'}</td></tr>
        </table><br>
        """
        delivery_details_text = f"""
    Delivery Details:
    Name: {full_name}
    Phone: {phone}
    Street: {address}
    City: {city}
    State: {state_abbr}
    Zip: {zip_code}
    Instructions: {special_instructions or 'N/A'}
    """

    discount_note_html = ""
    discount_note_text = ""
    if applied_discount and delivery_method.lower() == "pickup":
        discount_name = applied_discount.get("name", "Discount")
        discount_note_html = f"""
        <div style='margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 5px solid #ffc107;'>
            <h4 style='margin-top: 0;'>Discount Applied: {discount_name}</h4>
            <p>You saved <strong>${discount_amount:.2f}</strong> using <strong>{discount_name}</strong>.</p>
            <p><em>Please bring valid ID (student, military, medical) when picking up.</em></p>
        </div>
        """
        discount_note_text = f"""
    Discount Applied: {discount_name}
    You saved ${discount_amount:.2f} using {discount_name}.
    Please bring valid ID (student, military, medical) when picking up.
    """

    # Calc total with discounts and tax
    order_total = estimated_subtotal - (discount_amount if applied_discount else 0) + sales_tax

    # Build HTML body
    html_message = f"""
    <div style='font-family:Arial,sans-serif;'>
        <h2 style='color:#BB2D3B;'>Thank you for your order!</h2>
        <p><strong>Tracking ID:</strong> {order.tracking_id}</p>
        <h3 style='color:#BB2D3B;'>Order Fulfilled By:</h3>
        <table style='width:100%;background:#F8F9FA;'>
            <tr><td><strong>Store #:</strong></td><td>{store_info.store_number}</td></tr>
            <tr><td><strong>Address:</strong></td><td>{store_info.address}</td></tr>
            <tr><td><strong>City:</strong></td><td>{store_info.city}</td></tr>
            <tr><td><strong>State:</strong></td><td>{store_info.state}</td></tr>
            <tr><td><strong>Zip Code:</strong></td><td>{store_info.zip_code}</td></tr>
            <tr><td><strong>Phone:</strong></td><td>{store_info.phone}</td></tr>
            <tr><td><strong>Manager:</strong></td><td>{store_info.manager_name}</td></tr>
        </table><br>
        {delivery_details_html}
        {discount_note_html}
        <h3 style='color:#BB2D3B;'>Order Summary:</h3>
        <p><strong>Order Type:</strong> {delivery_method}</p>
        <table style='width:100%;border:1px solid #BB2D3B;background:#F8F9FA;'>
            <thead><tr style='background:#BB2D3B;color:#fff;'><th>Item Description</th></tr></thead>
            <tbody>{''.join([f"<tr><td>{line}</td></tr>" for line in order_lines])}</tbody>
        </table>
        <h3 style='color:#BB2D3B;'>Payment Summary:</h3>
        <table style='width:100%;background:#F8F9FA;'>
            <tr><td><strong>Subtotal:</strong></td><td>${estimated_subtotal:.2f}</td></tr>
            {f"<tr><td><strong>Discount:</strong></td><td>-${discount_amount:.2f}</td></tr>" if applied_discount else ""}
            <tr><td><strong>Sales Tax (7.25%):</strong></td><td>${sales_tax:.2f}</td></tr>
            <tr><td><strong>Total Paid:</strong></td><td>${order_total:.2f}</td></tr>

        </table>
        <p>If you have any questions, call us at <strong>{store_info.phone}</strong>.</p>
        <p style='color:#999;'>&copy; 2025 6th Street Pizza</p>
    </div>
    """

    # Build plain text version
    plain_message = f"""
    Thank you for your order!
    Tracking ID: {order.tracking_id}
    
    Order Fulfilled By:
    Store #: {store_info.store_number}
    Address: {store_info.address}
    City: {store_info.city}
    State: {store_info.state}
    Zip Code: {store_info.zip_code}
    Phone: {store_info.phone}
    Manager: {store_info.manager_name}
    
    {delivery_details_text}{discount_note_text}
    
    Order Summary:
    Order Type: {delivery_method}
    Items:
    {chr(10).join(f"- {line}" for line in order_lines)}
    
    Payment Summary:
    Subtotal: ${estimated_subtotal:.2f}
    {f"Discount: -${discount_amount:.2f}" if applied_discount else ""}
    Sales Tax (7.25%): ${sales_tax:.2f}
    Total Paid: ${order_total:.2f}

    
    If you have any questions, call us at {store_info.phone}.
    © 2025 6th Street Pizza
    """

    # Step 10: Send email using both plain text and HTML
    try:
        msg = EmailMultiAlternatives(
            subject="Your 6th Street Pizza Order Confirmation",
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        print("Email to customer failed:", e)

    # Step 11: Clean session
    request.session['cart'] = {}
    request.session.pop('applied_discount', None)
    for key in ["full_name", "email", "phone", "address", "city", "state", "zip", "special_instructions"]:
        request.session.pop(key, None)

    # Calculate updated total with tax and discount (no rounding)
    if applied_discount:
        adjusted_subtotal = estimated_subtotal - discount_amount
    else:
        adjusted_subtotal = estimated_subtotal

    updated_total = adjusted_subtotal + sales_tax

    # Update the order's total_price with recalculated value
    order.total_price = updated_total
    order.save(update_fields=["total_price"])
    try:
        summary = json.loads(order.order_summary)
        summary["total_price"] = float(updated_total)
        order.order_summary = json.dumps(summary, default=str)
        order.save(update_fields=["order_summary"])
    except Exception as e:
        print("Failed to update order summary total:", e)

    # Step 12: Render success
    return render(request, "payment_success.html", {
        "subtotal": estimated_subtotal,
        "discount_amount": discount_amount if applied_discount else None,
        "applied_discount": applied_discount,
        "sales_tax": sales_tax,
        "total": updated_total,
        "items": order_lines,
        "store_info": store_info,
        "order_type": delivery_method,
        "email": customer_email,
        "full_name": full_name,
        "phone": phone,
        "address": address,
        "city": city,
        "state": state_abbr,
        "zip": zip_code,
        "card_last4": request.session.get("card_last4"),
        "card_expiry": request.session.get("card_expiry"),
        "special_instructions": special_instructions,
        "toppings_json": json.dumps(get_all_toppings(), default=str),
        "tracking_id": order.tracking_id,
    })


# Store payment info
@csrf_exempt
def store_payment_details(request):
    print(" Stripe called /store-payment-details/")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            intent_id = data.get("paymentIntentId")
            intent = stripe.PaymentIntent.retrieve(
                intent_id, expand=["charges.data.payment_method_details"]
            )

            charge = intent.charges.data[0]
            card_info = charge.payment_method_details.get("card", {})

            # Fallbacks in case Stripe omits something
            brand = card_info.get("brand", "Unknown")
            last4 = card_info.get("last4", "")
            exp_month = card_info.get("exp_month")
            exp_year = card_info.get("exp_year")
            expiry = f"{exp_month}/{exp_year}" if exp_month and exp_year else ""

            # Save in session
            request.session["card_type"] = brand
            request.session["card_last4"] = last4
            request.session["card_expiry"] = expiry
            request.session.modified = True  # ensure session is saved

            return JsonResponse({"status": "stored"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)


# Save card info into the session
@csrf_exempt
def store_card_info(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request.session["card_last4"] = data.get("last4")
            request.session["card_expiry"] = data.get("expiry")
            return JsonResponse({"status": "stored"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=405)


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
