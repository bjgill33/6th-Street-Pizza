"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from accounts import views
# from . import views
from accounts.views import update_cart
from accounts.views import set_location

from accounts.views import home, menu, payment, add_to_cart, get_cart, remove_from_cart, clear_cart, update_cart, get_cart_data, set_location, payment_success, create_payment_intent, track_order, locations_page, coupons_page


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path('menu/', menu, name='menu'),
    path('payment/', payment, name='payment'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/data/', get_cart_data, name='get_cart_data'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path("set-location/", set_location, name="set-location"),
    path('locations/', views.get_locations, name='get_locations'),
    path('payment-success/', payment_success, name='payment_success'),
    path("create-payment-intent/", create_payment_intent, name="create_payment_intent"),
    path("tracking/", track_order, name="track_order"),
    path("store-locations/", locations_page, name="store_locations"),
    path("coupons/", coupons_page, name="coupons"),
    path("clear-coupon/", views.clear_coupon, name="clear_coupon"),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("validate-coupon/", views.validate_coupon, name="validate_coupon"),





]

