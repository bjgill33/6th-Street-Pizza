# accounts/tests.py
from django.test import TestCase
from decimal import Decimal
from .models import CustomUser, Topping, Pizza, Order

class ModelTests(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            phone='+1234567890',
            address='123 Test St',
            password='testpass123'
        )
        self.assertEqual(user.email, 'testuser@example.com')

    def test_create_topping(self):
        topping = Topping.objects.create(name='Pepperoni', price=1.50)
        self.assertEqual(topping.name, 'Pepperoni')

    def test_create_pizza(self):
        topping = Topping.objects.create(name='Pepperoni', price=1.50)
        pizza = Pizza.objects.create(name='Pepperoni Pizza', base_price=10.00)
        pizza.toppings.add(topping)
        self.assertEqual(pizza.total_price(), Decimal('11.50'))

    def test_create_order(self):
        user = CustomUser.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            phone='+1234567890',
            address='123 Test St',
            password='testpass123'
        )
        topping = Topping.objects.create(name='Pepperoni', price=1.50)
        pizza = Pizza.objects.create(name='Pepperoni Pizza', base_price=10.00)
        pizza.toppings.add(topping)
        order = Order.objects.create(customer=user, total_price=pizza.total_price())
        order.pizzas.add(pizza)
        self.assertEqual(order.total_price, Decimal('11.50'))