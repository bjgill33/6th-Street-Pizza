import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator

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

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, help_text="Enter a valid email address.")
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, help_text="Enter a valid phone number (e.g., +1234567890).")
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'address']

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()

        # Phone number validation
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_regex.match(str(self.phone)):  # Ensure self.phone is a string
            raise ValidationError("Invalid phone number format. Please use the format: '+999999999'.")

# Pizza Model
class Pizza(models.Model):
    name = models.CharField(max_length=100)
    toppings = models.CharField(max_length=255, help_text="Enter toppings separated by commas.")
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Price cannot be negative.")],
        help_text="Enter a non-negative price."
    )

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # Ensure the price is not negative
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

# Order Model
class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pizzas = models.ManyToManyField(Pizza)
    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0, message="Total price cannot be negative.")],
        help_text="Enter a non-negative total price."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"

    def clean(self):
        super().clean()

        # Ensure the total price is not negative
        if self.total_price < 0:
            raise ValidationError("Total price cannot be negative.")
