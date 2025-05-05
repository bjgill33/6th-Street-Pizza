# Import for custom user model and permissions
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Import for defining models and model fields
from django.db import models

# Import to handle signals triggered after saving an object
from django.db.models.signals import post_save

# Import for connecting signals to a receiver function
from django.dispatch import receiver

# Import to dynamically get the currently active user model
from django.contrib.auth import get_user_model

# Import to raise validation errors when certain conditions are not met
from django.core.exceptions import ValidationError

# Import to generate universally unique identifiers (UUIDs)
import uuid

# Import to handle precise decimal calculations, especially for prices
import decimal

# Import to serialize/deserialize JSON data
import json

# Import to handle database integrity checks and avoid conflicts
from django.db import IntegrityError

# Import to group database operations into atomic transactions
from django.db import transaction

# Import state choices for US-based address fields from a custom choices.py file
from .choices import US_STATES

# Import utility to generate a unique tracking ID for orders
from .utils import generate_tracking_id


# ========================================
# DiscountCode Model for Special Discounts
# ========================================
class DiscountCode(models.Model):
    # Name of the discount (e.g., "Police Discount")
    name = models.CharField(max_length=100)

    # Detailed description of the offer
    description = models.TextField()

    # Unique code customers will enter (e.g., "YFHSCKV-COP")
    code = models.CharField(max_length=50, unique=True)

    # Discount amount in percentage (e.g., 10.00 for 10%)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    # Indicates if the discount is currently active
    is_active = models.BooleanField(default=True)

    def __str__(self):
        # String representation in admin and shell
        return f"{self.name} ({self.percentage}%)"


# ============================================
#  FUNCTION TO GENERATE TRACKING ID
# ============================================

# Generates a unique tracking ID for each order
def generate_tracking_id():
    part1 = uuid.uuid4().hex[:8].upper()
    part2 = uuid.uuid4().hex[:8].upper()
    last_digit = uuid.uuid4().int % 10
    return f"PIZZA-{part1}-{part2}-{last_digit}"


# ============================================
#  LOCATION
# ============================================

# Model to store restaurant location details
class RestaurantLocation(models.Model):
    STATUS_CHOICES = [
        ("Open", "Open"),
        ("Closed", "Closed"),
    ]

    store_number = models.PositiveIntegerField(unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    phone = models.CharField(max_length=15, unique=True)
    manager_name = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10, null=True, blank=True)  # ✅ It's present here
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Open")

    def __str__(self):
        return f"Store {self.store_number} - {self.city}, {self.state}"

    class Meta:
        db_table = "restaurant_locations"


# ============================================
#  CUSTOM USER MANAGEMENT
# ============================================

# Manager to handle user creation and superuser creation
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, phone, address, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a name")
        if not phone:
            raise ValueError("Users must have a phone number")
        if not address:
            raise ValueError("Users must have an address")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, phone=phone, address=address)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, address, password=None):
        user = self.create_user(email, name, phone, address, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Custom user model to manage user accounts
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone", "address"]

    def __str__(self):
        return self.email


# ============================================
#  GUEST USER SYSTEM (For Non-Registered Users)
# ============================================

class GuestUser(models.Model):
    id = models.BigAutoField(primary_key=True)  # Change from UUID to Integer
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Guest-{self.id}"


# ============================================
#  MENU ITEMS
# ============================================


# Model to store toppings information
class Topping(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Model to store pizza details and pricing
class Pizza(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price_small = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_medium = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_extra_large = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    image = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        return f"/static/{self.image}" if self.image else "/static/images/default_pizza.jpg"


# Model to store wing flavors and prices
class Wing(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        return f"/static/{self.image}" if self.image else "/static/images/default_wings.jpg"


# Model to store drink options and prices
class Drink(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        return f"/static/{self.image}" if self.image else "/static/images/default_drink.jpg"


# Model to store dessert items and prices
class Dessert(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def get_image_url(self):
        return f"/static/{self.image}" if self.image else "/static/images/default_dessert.jpg"


# ============================================
#  ORDER SYSTEM
# ============================================


# Model to handle order information, customer, and payment details
class Order(models.Model):
    customer = models.ForeignKey(
        get_user_model(),
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    guest = models.ForeignKey(
        GuestUser,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    email = models.EmailField(blank=True, null=True,
                              help_text="Guest email (if customer is not logged in)")

    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    subtotal_before_discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    sales_tax = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    coupon = models.CharField(max_length=50, null=True, blank=True)

    order_summary = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [("Pending", "Pending"), ("Completed", "Completed"), ("Cancelled", "Cancelled")]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    DELIVERY_METHOD_CHOICES = [("Pickup", "Pickup"), ("Delivery", "Delivery")]
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES, default="Pickup")

    # Required address fields for order delivery or pickup
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Full name for guest orders")
    address = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False, default="Raleigh")
    state = models.CharField(max_length=2, choices=US_STATES, blank=False, null=False, default="NC")
    zip_code = models.CharField(max_length=10, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)

    # Payment Details
    card_type = models.CharField(
        max_length=20,
        choices=[
            ("Visa", "Visa"),
            ("MasterCard", "MasterCard"),
            ("American Express", "American Express"),
            ("Discover", "Discover"),
            ("Other", "Other")
        ],
        null=True,
        blank=True,
        help_text="Select the type of credit card used."
    )
    card_last_four = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text="Last 4 digits of the card number."
    )
    card_expiry_date = models.CharField(max_length=7, null=True, blank=True, help_text="MM/YYYY format.")
    paypal_email = models.EmailField(null=True, blank=True, help_text="PayPal email if PayPal was used.")

    def get_masked_card_number(self):
        """ Returns a masked credit card number like ****-****-****-1234 """
        if self.card_last_four:
            return f"****-****-****-{self.card_last_four}"
        return "No Card on File"

    class Meta:
        db_table = "accounts_order"

    # Store information for the order
    restaurant_location = models.ForeignKey(
        RestaurantLocation,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Select the store fulfilling this order."
    )
    restaurant_address = models.CharField(max_length=255, null=True, blank=True)
    restaurant_city = models.CharField(max_length=100, null=True, blank=True)
    restaurant_state = models.CharField(max_length=2, choices=US_STATES, null=True, blank=True)
    restaurant_zip_code = models.CharField(max_length=10, null=True, blank=True)
    restaurant_phone = models.CharField(max_length=20, null=True, blank=True)

    # Notes and special instructions for the order
    special_instructions = models.TextField(null=True, blank=True)

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]
    payment_confirmation = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="Pending")

    # Unique tracking ID for each order
    tracking_id = models.CharField(max_length=25, unique=True, blank=True)

    def save(self, *args, **kwargs):
        """ Ensure Order is saved properly before querying related objects. """
        with transaction.atomic():  # Ensures all queries execute as a unit (monitor this -- when creating a cart with multiple similar items)

            #  Step 1: Ensure order is saved first to generate self.pk
            if not self.pk:
                super().save(*args, **kwargs)  # Save order first to ensure primary key exists

            #  Step 2: Assign guest or customer ID properly
            if not self.customer and not self.guest:
                guest = GuestUser.objects.create()
                self.guest = guest

            #  Step 3: Assign tracking ID if not set
            if not self.tracking_id:
                self.tracking_id = generate_tracking_id()

            #  Step 4: Populate restaurant details if a location is selected
            if self.restaurant_location:
                self.restaurant_address = self.restaurant_location.address
                self.restaurant_city = self.restaurant_location.city
                self.restaurant_state = self.restaurant_location.state
                self.restaurant_zip_code = self.restaurant_location.zip_code
                self.restaurant_phone = self.restaurant_location.phone

            #  Step 5: Ensure payment details are captured
            if self.card_last_four:
                self.card_last_four = self.card_last_four[-4:]  # Ensure only last 4 digits are stored

            # Step 6: Calculate total price before saving
            self.total_price = self.calculate_total_price()

            # Step 7: Ensure order summary is updated
            self.order_summary = self.generate_order_summary()

            #  Step 8: Save the order again, only updating specific fields
            super().save(update_fields=[
                "guest", "customer", "tracking_id", "order_summary",
                "total_price", "restaurant_address", "restaurant_city",
                "restaurant_state", "restaurant_zip_code", "restaurant_phone",
                "card_type", "card_last_four", "card_expiry_date", "paypal_email"
            ])

    def generate_order_summary(self):
        """
        Generate a structured JSON summary of the order,
        including customer/store info, items, discount, tax, and totals.
        """

        # ---------------------------------------------
        # Build base customer and store location data
        # ---------------------------------------------
        order_data = {
            "customer_id": self.customer.id if self.customer else None,
            "guest_id": self.guest.id if self.guest else None,
            "email": self.customer.email if self.customer else (self.email if self.email else "No Email Provided"),
            "name": self.customer.name if self.customer else (self.name if self.name else "Guest"),
            "phone": self.phone,
            "address": {
                "street": self.address,
                "city": self.city,
                "zipcode": self.zip_code,
                "state": self.state,
            },
            "store_location": {
                "store_number": self.restaurant_location.store_number if self.restaurant_location else "Not Assigned",
                "address": {
                    "street": self.restaurant_location.address if self.restaurant_location else "N/A",
                    "city": self.restaurant_location.city if self.restaurant_location else "N/A",
                    "state": self.restaurant_location.state if self.restaurant_location else "N/A",
                }
            },
            "special_instructions": self.special_instructions if self.special_instructions else "None",
            "tracking_id": self.tracking_id,
        }

        # ---------------------------------------------
        # Build order items (pizzas, wings, drinks, desserts)
        # ---------------------------------------------
        order_data["order"] = {
            "pizzas": [
                {
                    "name": item.pizza.name,
                    "size": item.size,
                    "quantity": item.quantity,
                    "toppings": list(filter(None, [
                        item.topping_1.name if item.topping_1 else None,
                        item.topping_2.name if item.topping_2 else None,
                        item.topping_3.name if item.topping_3 else None
                    ]))
                }
                for item in self.orderpizza_set.all()
            ],
            "wings": [
                {"flavor": item.wing.name, "quantity": item.quantity}
                for item in self.orderwings_set.all()
            ],
            "drinks": [
                {"name": item.drink.name, "quantity": item.quantity}
                for item in self.orderdrinks_set.all()
            ],
            "desserts": [
                {"name": item.dessert.name, "quantity": item.quantity}
                for item in self.orderdesserts_set.all()
            ],
        }

        # ---------------------------------------------
        # Add pricing: subtotal, discount, tax, coupon
        # ---------------------------------------------
        final_total = float(self.total_price)  # This is what was paid
        tax_rate = 0.0725  # NC tax
        coupon_code = None
        discount_percentage = 0.0
        discount_amount = 0.0
        sales_tax = 0.0

        if hasattr(self, "_applied_discount"):
            discount_info = self._applied_discount
            discount_percentage = float(discount_info.get("percentage", 0))
            coupon_code = discount_info.get("code") or discount_info.get("name")

            subtotal = final_total / (1 + tax_rate)
            discount_amount = (subtotal * discount_percentage) / (100 - discount_percentage)
            subtotal += discount_amount
            sales_tax = (subtotal - discount_amount) * tax_rate

            order_data["coupon"] = {
                "code": coupon_code,
                "percentage": discount_percentage
            }
        else:
            subtotal = final_total / (1 + tax_rate)
            sales_tax = subtotal * tax_rate
            order_data["coupon"] = None

        final_price = subtotal + sales_tax

        # Remove detailed tax/discount lines from final summary
        order_data["subtotal_before_tax_and_discount"] = final_price
        order_data["tax_rate"] = tax_rate

        return json.dumps(order_data)

    def calculate_total_price(self):
        """ Calculate the total price of the order based on items. """
        total = sum(
            item.get_price() for item in self.orderpizza_set.all()
        ) + sum(
            item.get_price() for item in self.orderwings_set.all()
        ) + sum(
            item.get_price() for item in self.orderdrinks_set.all()
        ) + sum(
            item.get_price() for item in self.orderdesserts_set.all()
        )
        return total  # ✅ Return the total price (do not save inside this method)


@receiver(post_save, sender=Order)
def update_order_total(sender, instance, **kwargs):
    """Automatically update the total price when an order is saved."""
    new_total = instance.calculate_total_price()
    Order.objects.filter(pk=instance.pk).update(total_price=new_total)


# ============================================
#  ORDER ITEMS
# ============================================

# Manages pizza orders with toppings and size.
class OrderPizza(models.Model):
    SIZE_CHOICES = [
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
        ("extra_large", "Extra Large")
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderpizza_set")
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    size = models.CharField(max_length=15, choices=SIZE_CHOICES, default="Small")
    quantity = models.PositiveIntegerField(default=1)

    topping_1 = models.ForeignKey(Topping, on_delete=models.SET_NULL, null=True, blank=True, related_name="topping_1")
    topping_2 = models.ForeignKey(Topping, on_delete=models.SET_NULL, null=True, blank=True, related_name="topping_2")
    topping_3 = models.ForeignKey(Topping, on_delete=models.SET_NULL, null=True, blank=True, related_name="topping_3")

    def get_price(self):
        base_price = {
            "small": self.pizza.price_small,
            "medium": self.pizza.price_medium,
            "large": self.pizza.price_large,
            "extra_large": self.pizza.price_extra_large
        }.get(self.size, self.pizza.price_large)

        topping_price = sum(filter(None, [
            self.topping_1.price if self.topping_1 else 0,
            self.topping_2.price if self.topping_2 else 0,
            self.topping_3.price if self.topping_3 else 0
        ])) * self.quantity

        return (base_price + topping_price) * self.quantity

    def save(self, *args, **kwargs):
        """ Ensure duplicate pizzas merge instead of raising an IntegrityError. """
        try:
            # ✅ Look for an existing identical pizza order in the same order
            existing_pizza = OrderPizza.objects.filter(
                order=self.order,
                pizza=self.pizza,
                size=self.size,
                topping_1=self.topping_1,
                topping_2=self.topping_2,
                topping_3=self.topping_3
            ).exclude(pk=self.pk).first()

            if existing_pizza:
                # ✅ Merge quantities instead of duplicating
                existing_pizza.quantity += self.quantity
                existing_pizza.save(update_fields=["quantity"])
                return  # ✅ Exit early to prevent duplicate save

            super().save(*args, **kwargs)  # Normal save if no duplicate found

        except IntegrityError:
            pass  # ✅ Prevents failure if a race condition occurs

    class Meta:
        db_table = "accounts_order_pizzas"


# Stores additional toppings for pizzas.
class OrderPizzaTopping(models.Model):
    order_pizza = models.ForeignKey(OrderPizza, on_delete=models.CASCADE)
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Allowing topping quantities

    class Meta:
        db_table = "accounts_order_pizza_toppings"


# Handle wing, drink, and dessert items with price
class OrderWings(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    wing = models.ForeignKey(Wing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Add quantity field

    def get_price(self):
        return self.wing.price * self.quantity

    class Meta:
        db_table = "accounts_order_wings"


class OrderDrinks(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Add quantity field

    def get_price(self):
        return self.drink.price * self.quantity

    class Meta:
        db_table = "accounts_order_drinks"


class OrderDesserts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dessert = models.ForeignKey(Dessert, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Add quantity field

    def get_price(self):
        return self.dessert.price * self.quantity

    class Meta:
        db_table = "accounts_order_desserts"


# Ensures the total price is automatically recalculated after changes.
@receiver(post_save, sender=Order)
def update_order_total(sender, instance, **kwargs):
    new_total = instance.calculate_total_price()
    Order.objects.filter(pk=instance.pk).update(total_price=new_total)
