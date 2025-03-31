from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# ============================================
#  FUNCTION TO GENERATE TRACKING ID
# ============================================

def generate_tracking_id():
    part1 = uuid.uuid4().hex[:8].upper()
    part2 = uuid.uuid4().hex[:8].upper()
    last_digit = uuid.uuid4().int % 10
    return f"PIZZA-{part1}-{part2}-{last_digit}"


# ============================================
#  LOCATION
# ============================================

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Open")

    def __str__(self):
        return f"Store {self.store_number} - {self.city}, {self.state}"

    class Meta:
        db_table = "restaurant_locations"


# ============================================
#  CUSTOM USER MANAGEMENT
# ============================================

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

class Topping(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Pizza(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    toppings = models.ManyToManyField(Topping)

    price_small = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_medium = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_large = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_extra_large = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Wing(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Drink(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


class Dessert(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


# ============================================
#  U.S States
# ============================================


# US States Choices
US_STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
    ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"), ("ID", "Idaho"),
    ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
    ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
    ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"),
    ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"),
    ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"),
    ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"),
    ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
    ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"), ("WV", "West Virginia"),
    ("WI", "Wisconsin"), ("WY", "Wyoming")
]


# ============================================
#  ORDER SYSTEM
# ============================================

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

    email = models.EmailField(blank=True, null=True, help_text="Guest email (if customer is not logged in)")  # Added guest email field

    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    order_summary = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [("Pending", "Pending"), ("Completed", "Completed"), ("Cancelled", "Cancelled")]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    DELIVERY_METHOD_CHOICES = [("Pickup", "Pickup"), ("Delivery", "Delivery")]
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES, default="Pickup")

    # REQUIRED ADDRESS FIELDS
    address = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False, default="Raleigh")
    state = models.CharField(max_length=2, choices=US_STATES, blank=False, null=False, default="NC")
    zip_code = models.CharField(max_length=10, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)

    # Notes
    special_instructions = models.TextField(null=True, blank=True)

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    ]
    payment_confirmation = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="Pending")

    tracking_id = models.CharField(max_length=25, unique=True, blank=True)

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
        return total

    def save(self, *args, **kwargs):
        """ Ensure Order is saved before querying related objects. """

        # Assign GuestUser if no customer is selected
        if not self.customer and not self.guest:
            guest = GuestUser.objects.create()
            self.guest = guest  # Assign guest ID

        # Generate tracking ID if not set
        if not self.tracking_id:
            self.tracking_id = generate_tracking_id()

        # Save the order first to generate the ID before querying related items
        super().save(*args, **kwargs)

        # Now calculate the total price using related objects
        self.total_price = self.calculate_total_price()

        # Save again to update total price
        super().save(update_fields=['total_price'])


@receiver(post_save, sender=Order)
def update_order_total(sender, instance, **kwargs):
    """Automatically update the total price when an order is saved."""
    new_total = instance.calculate_total_price()
    Order.objects.filter(pk=instance.pk).update(total_price=new_total)


# ============================================
#  ORDER ITEMS
# ============================================

''' old view for pizzas
class OrderPizza(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    size = models.CharField(max_length=15, choices=[("small", "Small"), ("large", "Large")], default="large")
    quantity = models.PositiveIntegerField(default=1)

    def get_price(self):
        return self.pizza.price_large * self.quantity

    class Meta:
        db_table = "accounts_order_pizzas"
'''


class OrderPizza(models.Model):
    SIZE_CHOICES = [
        ("small", "Small"),
        ("medium", "Medium"),  # ✅ Added Medium
        ("large", "Large"),
        ("extra_large", "Extra Large")  # ✅ Added Extra Large
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    toppings = models.ManyToManyField(Topping, through='OrderPizzaTopping')  # ✅ New M2M relationship
    size = models.CharField(max_length=15, choices=SIZE_CHOICES, default="large")
    quantity = models.PositiveIntegerField(default=1)

    def get_price(self):
        base_price = {
            "small": self.pizza.price_small,
            "medium": self.pizza.price_medium,  # ✅ Medium price
            "large": self.pizza.price_large,
            "extra_large": self.pizza.price_extra_large  # ✅ Extra Large price
        }.get(self.size, self.pizza.price_large)

        topping_price = sum(topping.price for topping in self.toppings.all())  # ✅ Add topping costs

        return (base_price + topping_price) * self.quantity

    class Meta:
        db_table = "accounts_order_pizzas"



class OrderPizzaTopping(models.Model):
    order_pizza = models.ForeignKey(OrderPizza, on_delete=models.CASCADE)
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # ✅ Allowing topping quantities

    class Meta:
        db_table = "accounts_order_pizza_toppings"










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


@receiver(post_save, sender=Order)
def update_order_total(sender, instance, **kwargs):
    new_total = instance.calculate_total_price()
    Order.objects.filter(pk=instance.pk).update(total_price=new_total)
