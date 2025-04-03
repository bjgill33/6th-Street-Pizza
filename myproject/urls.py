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
from . import views
from accounts.views import update_cart

from accounts.views import home, menu, payment, add_to_cart, get_cart, remove_from_cart, clear_cart, update_cart, get_cart_data


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
]

