from django.contrib import admin
from .models import CustomUser, Topping, Pizza, Wing, Drink, Dessert, Order, OrderPizza, OrderWings, OrderDrinks, \
    OrderDesserts, GuestUser, RestaurantLocation, generate_tracking_id, OrderPizzaTopping
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib import messages
from django import forms
from django.forms import ModelChoiceField


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
#  PIZZA ADMIN PANEL CONFIGURATION
# ============================================

class PizzaAdmin(admin.ModelAdmin):
    """ Admin panel for managing pizzas """
    list_display = ('name', 'description', 'price_small', 'price_medium', 'price_large', 'price_extra_large')
    list_display_links = ('name',)  # ✅ Make name clickable
    list_editable = ('description', 'price_small', 'price_medium', 'price_large', 'price_extra_large')
    search_fields = ('name', 'description')
    #filter_horizontal = ('toppings',)
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
    """ Inline for managing Pizza orders inside OrderAdmin """
    model = OrderPizza
    extra = 1
    fields = ('pizza', 'size', 'quantity', 'topping_1', 'topping_2', 'topping_3')
    autocomplete_fields = ('pizza', 'topping_1', 'topping_2', 'topping_3')

    formfield_overrides = {
        models.ForeignKey: {'widget': forms.Select}
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Modify topping dropdowns to show price in choices """
        if db_field.name in ["topping_1", "topping_2", "topping_3"]:
            return forms.ModelChoiceField(
                queryset=Topping.objects.all().order_by("name"),
                required=False,
                empty_label="(No Topping)",
                to_field_name="id",
                widget=forms.Select(),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """ Optimize queryset retrieval to prevent querying unsaved orders """
        qs = super().get_queryset(request)
        order_id = request.resolver_match.kwargs.get('object_id')
        return qs.filter(order_id=order_id) if order_id else qs.none()


class OrderWingsInline(admin.TabularInline):
    """ Inline for managing Wing orders inside OrderAdmin """
    model = OrderWings
    extra = 1
    fields = ('wing', 'quantity')
    autocomplete_fields = ('wing',)

    def get_queryset(self, request):
        """ Optimize queryset retrieval to prevent querying unsaved orders """
        qs = super().get_queryset(request)
        order_id = request.resolver_match.kwargs.get('object_id')
        return qs.filter(order_id=order_id) if order_id else qs.none()


class OrderDrinksInline(admin.TabularInline):
    """ Inline for managing Drink orders inside OrderAdmin """
    model = OrderDrinks
    extra = 1
    fields = ('drink', 'quantity')
    autocomplete_fields = ('drink',)

    def get_queryset(self, request):
        """ Optimize queryset retrieval to prevent querying unsaved orders """
        qs = super().get_queryset(request)
        order_id = request.resolver_match.kwargs.get('object_id')
        return qs.filter(order_id=order_id) if order_id else qs.none()


class OrderDessertsInline(admin.TabularInline):
    """ Inline for managing Dessert orders inside OrderAdmin """
    model = OrderDesserts
    extra = 1
    fields = ('dessert', 'quantity')
    autocomplete_fields = ('dessert',)

    def get_queryset(self, request):
        """ Optimize queryset retrieval to prevent querying unsaved orders """
        qs = super().get_queryset(request)
        order_id = request.resolver_match.kwargs.get('object_id')
        return qs.filter(order_id=order_id) if order_id else qs.none()


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
        "customer", "get_guest_email", "restaurant_location", "restaurant_city", "restaurant_state",
        "name", "city", "state", "zip_code", "phone", "status", "total_price",
        "created_at", "tracking_id", "get_masked_card_number", "payment_confirmation",
    )

    list_filter = ("status", "delivery_method", "payment_confirmation", "state")
    search_fields = ("customer__email", "email", "name", "status", "tracking_id", "city", "zip_code", "phone")
    readonly_fields = (
        "tracking_id", "order_summary", "total_price", "get_masked_card_number",
        "restaurant_address", "restaurant_city", "restaurant_state", "restaurant_zip_code", "restaurant_phone",
    )

    fieldsets = (
        ("Customer Information", {
            "fields": ("customer", "guest", "name", "email"),
        }),
        ("Order Details", {
            "fields": ("status", "delivery_method", "payment_confirmation", "restaurant_location"),
        }),
        ("Address Information", {
            "fields": ("address", "city", "state", "zip_code", "phone"),
        }),
        ("Additional Information", {
            "fields": ("special_instructions",),
        }),
        ("Payment Details", {
            "fields": ("card_type", "card_last_four", "card_expiry_date", "paypal_email"),
        }),
        ("Order Summary", {
            "fields": ("order_summary", "total_price", "tracking_id"),  # ✅ Moved total_price here
        }),
    )

    inlines = [OrderPizzaInline, OrderWingsInline, OrderDrinksInline, OrderDessertsInline]

    def get_guest_email(self, obj):
        """ Returns guest email if available, otherwise customer's email """
        return obj.email if obj.email else (obj.customer.email if obj.customer else "Guest")

    get_guest_email.short_description = "Guest Email"

    def save_model(self, request, obj, form, change):
        """ Ensure Order instance is saved before accessing related objects. """

        if not obj.city or not obj.state or not obj.zip_code or not obj.phone:
            raise ValidationError("City, State, Zip Code, and Phone are required fields.")

        # Ensure tracking ID is set before saving
        if not obj.tracking_id:
            obj.tracking_id = generate_tracking_id()

        # ✅ Save the order FIRST before querying related objects
        if not obj.pk:
            super().save_model(request, obj, form, change)

        obj.refresh_from_db()  # Ensure primary key is assigned

    def save_related(self, request, form, formsets, change):
        """ Ensure Order instance is saved before dealing with related objects """
        obj = form.instance
        if not obj.pk:
            obj.save()  # Ensure Order instance has a primary key

        super().save_related(request, form, formsets, change)

        # ✅ Ensure at least one item is in the order
        if not (
                obj.orderpizza_set.exists() or obj.orderwings_set.exists() or obj.orderdrinks_set.exists() or obj.orderdesserts_set.exists()):
            messages.warning(request, "This order does not contain any items.")

        # ✅ Calculate total price after inlines are saved
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
#  TOPPINGS ADMIN PANEL CONFIGURATION
# ============================================
@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    """ Admin panel for managing toppings """
    list_display = ('name', 'price', 'description')  # ✅ Shows price & description
    list_editable = ('price', 'description')  # ✅ Allows inline editing
    search_fields = ('name', 'description')  # ✅ Enables searching by name & description
    list_per_page = 20
    actions = ['delete_selected']


# ============================================
#  GUEST USER ADMIN PANEL CONFIGURATION
# ============================================

admin.site.register(GuestUser)

admin.site.register(Order, OrderAdmin)
