from django.contrib import admin

from .models import CustomUser, Topping, Pizza, Order

# Register the CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone', 'address', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('email', 'name', 'phone')
    list_filter = ('is_active', 'is_staff', 'is_admin')

admin.site.register(CustomUser, CustomUserAdmin)

# Register the Topping model
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Topping, ToppingAdmin)

# Register the Pizza model
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    filter_horizontal = ('toppings',)  # For selecting toppings in the admin

admin.site.register(Pizza, PizzaAdmin)

# Register the Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'total_price', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer__email', 'status')
    date_hierarchy = 'created_at'

admin.site.register(Order, OrderAdmin)
