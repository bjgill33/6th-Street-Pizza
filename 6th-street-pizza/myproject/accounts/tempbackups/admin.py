from django.contrib import admin
from .models import CustomUser, Topping, Pizza, Wing, Drink, Dessert, Order, OrderPizza, OrderWings, OrderDrinks, \
    OrderDesserts, GuestUser, RestaurantLocation, generate_tracking_id, OrderPizzaTopping
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from django import forms


# ============================================
#  CUSTOM USER ADMIN PANEL CONFIGURATION
# ============================================

class CustomUserAdmin(admin.ModelAdmin):
    """ Admin panel configuration for CustomUser model """
    list_display = ('email', 'name', 'phone', 'address', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('email', 'name', 'phone')
    list_filter = ('is_active', 'is_staff', 'is_admin')


admin.site.register(CustomUser, CustomUserAdmin)


# ============================================
#  TOPPING ADMIN PANEL CONFIGURATION
# ============================================

class ToppingAdmin(admin.ModelAdmin):
    """ Admin panel for managing pizza toppings """
    list_display = ('name', 'price', 'description')
    list_editable = ('price', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20  # Paginate results for better usability
    actions = ['delete_selected']  # Enable bulk deletion


admin.site.register(Topping, ToppingAdmin)


# ============================================
#  PIZZA ADMIN PANEL CONFIGURATION
# ============================================

class PizzaAdmin(admin.ModelAdmin):
    """ Admin panel for managing pizzas """
    list_display = ('name', 'description', 'price_small', 'price_medium', 'price_large', 'price_extra_large')
    list_display_links = ('name',)  # ✅ Make name clickable
    list_editable = ('description', 'price_small', 'price_medium', 'price_large', 'price_extra_large')
    search_fields = ('name', 'description')
    filter_horizontal = ('toppings',)
    list_per_page = 20
    actions = ['delete_selected']


admin.site.register(Pizza, PizzaAdmin)


# ============================================
#  WINGS ADMIN PANEL CONFIGURATION
# ============================================

class WingAdmin(admin.ModelAdmin):
    """ Admin panel for managing wings """
    list_display = ('name', 'price', 'description')
    list_display_links = ('name',)
    list_editable = ('price', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20
    actions = ['delete_selected']


admin.site.register(Wing, WingAdmin)


# ============================================
#  DRINKS ADMIN PANEL CONFIGURATION
# ============================================

class DrinkAdmin(admin.ModelAdmin):
    """ Admin panel for managing drinks """
    list_display = ('name', 'price', 'description')
    list_display_links = ('name',)
    list_editable = ('price', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20
    actions = ['delete_selected']


admin.site.register(Drink, DrinkAdmin)


# ============================================
#  DESSERTS ADMIN PANEL CONFIGURATION
# ============================================

class DessertAdmin(admin.ModelAdmin):
    """ Admin panel for managing desserts """
    list_display = ('name', 'price', 'description')
    list_display_links = ('name',)
    list_editable = ('price', 'description')
    search_fields = ('name', 'description')
    list_per_page = 20
    actions = ['delete_selected']


admin.site.register(Dessert, DessertAdmin)


# ============================================
#  INLINE CLASSES FOR ORDER ITEMS
# ============================================

class OrderToppingsInline(admin.TabularInline):
    """ Inline form for toppings inside OrderAdmin """
    model = OrderPizzaTopping
    extra = 1
    fields = ('order_pizza', 'topping', 'quantity')
    autocomplete_fields = ('topping', 'order_pizza')


class OrderPizzaInline(admin.TabularInline):
    """ Inline for Pizza orders inside OrderAdmin """
    model = OrderPizza
    extra = 1
    fields = ('pizza', 'size', 'quantity')
    autocomplete_fields = ('pizza',)


class OrderWingsInline(admin.TabularInline):
    """ Inline for Wing orders inside OrderAdmin """
    model = OrderWings
    extra = 1
    fields = ('wing', 'quantity')
    autocomplete_fields = ('wing',)


class OrderDrinksInline(admin.TabularInline):
    """ Inline for Drink orders inside OrderAdmin """
    model = OrderDrinks
    extra = 1
    fields = ('drink', 'quantity')
    autocomplete_fields = ('drink',)


class OrderDessertsInline(admin.TabularInline):
    """ Inline for Dessert orders inside OrderAdmin """
    model = OrderDesserts
    extra = 1
    fields = ('dessert', 'quantity')
    autocomplete_fields = ('dessert',)


# ============================================
#  ORDER ADMIN PANEL CONFIGURATION
# ============================================

class OrderAdminForm(forms.ModelForm):
    """ Custom form for OrderAdmin to allow manual email entry for guests. """

    class Meta:
        model = Order
        fields = '__all__'  # Keep all fields from Order

    def clean_email(self):
        """ Validate guest email entry. """
        email = self.cleaned_data.get("email")
        customer = self.cleaned_data.get("customer")

        if email and customer:
            raise ValidationError("You cannot set both a registered customer and a guest email.")

        return email


class OrderAdmin(admin.ModelAdmin):
    """ Admin panel for managing orders """
    form = OrderAdminForm  # Use custom form

    list_display = (
        "customer", "guest_email", "city", "state", "zip_code", "phone", "status", "total_price", "created_at",
        "tracking_id",
        "payment_confirmation"
    )
    list_filter = ("status", "delivery_method", "payment_confirmation", "state")
    search_fields = ("customer_email", "guest_email", "status", "tracking_id", "city", "zip_code", "phone")
    readonly_fields = ("total_price", "tracking_id", "order_summary")

    fieldsets = (
        ("Customer Information", {
            "fields": ("customer", "guest", "email"),
        }),
        ("Order Details", {
            "fields": ("status", "delivery_method", "payment_confirmation"),
        }),
        ("Address Information", {
            "fields": ("address", "city", "state", "zip_code", "phone"),
        }),
        ("Additional Information", {
            "fields": ("special_instructions",),
        }),
        ("Order Summary", {
            "fields": ("order_summary", "tracking_id"),
        }),
    )

    inlines = [OrderPizzaInline, OrderWingsInline, OrderDrinksInline, OrderDessertsInline]

    def guest_email(self, obj):
        """ Returns the guest's email if available, otherwise the customer's email. """
        return obj.email if obj.email else (obj.customer.email if obj.customer else "Guest")

    guest_email.short_description = "Guest Email"
    guest_email.admin_order_field = "email"

    def save_model(self, request, obj, form, change):
        """ Ensure all required fields are filled out before saving. """

        if not obj.city or not obj.state or not obj.zip_code or not obj.phone:
            raise ValidationError("City, State, Zip Code, and Phone are required fields.")

        # Ensure tracking ID is set before saving
        if not obj.tracking_id:
            obj.tracking_id = generate_tracking_id()

        # ✅ Save the order FIRST before querying related objects
        super().save_model(request, obj, form, change)

        # ✅ Ensure at least one item is in the order AFTER saving
        if not obj.pk:  # Ensure object has a primary key
            obj.refresh_from_db()  # Get the primary key if it wasn't assigned immediately

        if (
                not obj.orderpizza_set.exists() and
                not obj.orderwings_set.exists() and
                not obj.orderdrinks_set.exists() and
                not obj.orderdesserts_set.exists()
        ):
            messages.warning(request, "This order does not contain any items.")

        # ✅ Calculate total price AFTER the order is saved
        if hasattr(obj, "calculate_total_price"):
            obj.total_price = obj.calculate_total_price()
            obj.save(update_fields=["total_price"])
        else:
            raise AttributeError("The Order model must have a 'calculate_total_price' method.")

    def save_related(self, request, form, formsets, change):
        """ Ensure at least one item exists AFTER inlines are saved. """
        super().save_related(request, form, formsets, change)

        obj = form.instance  # Get the instance from the form

        # Ensure at least one item is in the order
        if not obj.orderpizza_set.exists() and not obj.orderwings_set.exists() and not obj.orderdrinks_set.exists() and not obj.orderdesserts_set.exists():
            messages.warning(request, "This order does not contain any items.")

        # Calculate total price now that items are saved
        if hasattr(obj, "calculate_total_price"):
            obj.total_price = obj.calculate_total_price()
            obj.save(update_fields=["total_price"])
        else:
            raise AttributeError("The Order model must have a 'calculate_total_price' method.")


# ============================================
#  RESTAURANT LOCATION ADMIN PANEL CONFIGURATION
# ============================================

@admin.register(RestaurantLocation)
class RestaurantLocationAdmin(admin.ModelAdmin):
    """ Admin panel for managing restaurant locations """
    list_display = ("store_number", "city", "state", "phone", "manager_name", "status")
    list_filter = ("status", "city", "state")
    search_fields = ("store_number", "manager_name", "city", "state", "phone")
    ordering = ("store_number",)
    list_editable = ("status", "manager_name", "phone")  # ✅ Allows inline editing in the admin list view
    actions = ['delete_selected']


# ============================================
#  GUEST USER ADMIN PANEL CONFIGURATION
# ============================================

admin.site.register(GuestUser)
admin.site.register(Order, OrderAdmin)
