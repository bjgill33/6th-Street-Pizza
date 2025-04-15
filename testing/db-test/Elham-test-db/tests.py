from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
import json
from .models import (
    RestaurantLocation,
    CustomUser,
    GuestUser,
    Topping,
    Pizza,
    Wing,
    Drink,
    Dessert,
    Order,
    OrderPizza,
    OrderWings,
    OrderDrinks,
    OrderDesserts
)

User = get_user_model()


class RestaurantLocationTests(TestCase):
    def setUp(self):
        self.location = RestaurantLocation.objects.create(
            store_number=1,
            address="123 Main St",
            city="Raleigh",
            state="NC",
            phone="555-1234",
            manager_name="John Doe",
            zip_code="27601"
        )

    def test_restaurant_location_creation(self):
        self.assertEqual(self.location.store_number, 1)
        self.assertEqual(self.location.city, "Raleigh")
        self.assertEqual(self.location.status, "Open")
        self.assertEqual(str(self.location), "Store 1 - Raleigh, NC")

    def test_unique_store_number(self):
        with self.assertRaises(Exception):
            RestaurantLocation.objects.create(
                store_number=1,  # Duplicate store number
                address="456 Oak St",
                city="Durham",
                state="NC",
                phone="555-5678",
                manager_name="Jane Smith"
            )


class CustomUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            phone="555-1234",
            address="123 Main St",
            password="testpass123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.name, "Test User")
        self.assertFalse(self.user.is_admin)
        self.assertTrue(self.user.is_active)

    def test_superuser_creation(self):
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            name="Admin User",
            phone="555-4321",
            address="456 Admin Ave",
            password="adminpass123"
        )
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                name="Test User",
                phone="555-1234",
                address="123 Main St",
                password="testpass123"
            )


class GuestUserTests(TestCase):
    def test_guest_user_creation(self):
        guest = GuestUser.objects.create()
        self.assertIsNotNone(guest.id)
        self.assertEqual(str(guest), f"Guest-{guest.id}")


class MenuItemTests(TestCase):
    def setUp(self):
        # Create toppings
        self.topping1 = Topping.objects.create(name="Pepperoni", price=Decimal('1.50'))
        self.topping2 = Topping.objects.create(name="Mushrooms", price=Decimal('1.00'))

        # Create pizza
        self.pizza = Pizza.objects.create(
            name="Margherita",
            description="Classic margherita pizza",
            price_small=Decimal('10.99'),
            price_medium=Decimal('12.99'),
            price_large=Decimal('14.99'),
            price_extra_large=Decimal('16.99')
        )

        # Create wings
        self.wings = Wing.objects.create(
            name="Buffalo",
            price=Decimal('8.99'),
            description="Spicy buffalo wings"
        )

        # Create drink
        self.drink = Drink.objects.create(
            name="Coke",
            price=Decimal('1.99'),
            description="Regular Coke"
        )

        # Create dessert
        self.dessert = Dessert.objects.create(
            name="Chocolate Cake",
            price=Decimal('4.99'),
            description="Rich chocolate cake"
        )

    def test_topping_creation(self):
        self.assertEqual(self.topping1.name, "Pepperoni")
        self.assertEqual(self.topping1.price, Decimal('1.50'))
        self.assertEqual(str(self.topping1), "Pepperoni")

    def test_pizza_creation(self):
        self.assertEqual(self.pizza.name, "Margherita")
        self.assertEqual(self.pizza.price_large, Decimal('14.99'))
        self.assertEqual(str(self.pizza), "Margherita")

    def test_pizza_image_url(self):
        self.pizza.image = "pizzas/margherita.jpg"
        self.assertEqual(self.pizza.get_image_url, "/static/pizzas/margherita.jpg")

    def test_wings_creation(self):
        self.assertEqual(self.wings.name, "Buffalo")
        self.assertEqual(self.wings.price, Decimal('8.99'))
        self.assertEqual(str(self.wings), "Buffalo")

    def test_drink_creation(self):
        self.assertEqual(self.drink.name, "Coke")
        self.assertEqual(self.drink.price, Decimal('1.99'))
        self.assertEqual(str(self.drink), "Coke")

    def test_dessert_creation(self):
        self.assertEqual(self.dessert.name, "Chocolate Cake")
        self.assertEqual(self.dessert.price, Decimal('4.99'))
        self.assertEqual(str(self.dessert), "Chocolate Cake")


class OrderTests(TestCase):
    def setUp(self):
        # Create location
        self.location = RestaurantLocation.objects.create(
            store_number=1,
            address="123 Main St",
            city="Raleigh",
            state="NC",
            phone="555-1234",
            manager_name="John Doe"
        )

        # Create user
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            phone="555-1234",
            address="123 Main St",
            password="testpass123"
        )

        # Create guest
        self.guest = GuestUser.objects.create()

        # Create menu items
        self.pizza = Pizza.objects.create(
            name="Margherita",
            description="Classic margherita pizza",
            price_small=Decimal('10.99'),
            price_medium=Decimal('12.99'),
            price_large=Decimal('14.99')
        )

        self.topping1 = Topping.objects.create(name="Pepperoni", price=Decimal('1.50'))
        self.topping2 = Topping.objects.create(name="Mushrooms", price=Decimal('1.00'))

        self.wings = Wing.objects.create(
            name="Buffalo",
            price=Decimal('8.99'),
            description="Spicy buffalo wings"
        )

        self.drink = Drink.objects.create(
            name="Coke",
            price=Decimal('1.99'),
            description="Regular Coke"
        )

        self.dessert = Dessert.objects.create(
            name="Chocolate Cake",
            price=Decimal('4.99'),
            description="Rich chocolate cake"
        )

        # Create order
        self.order = Order.objects.create(
            customer=self.user,
            address="123 Main St",
            city="Raleigh",
            state="NC",
            zip_code="27601",
            phone="555-1234",
            restaurant_location=self.location,
            delivery_method="Pickup",
            card_type="Visa",
            card_last_four="1234"
        )

    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.status, "Pending")
        self.assertEqual(self.order.delivery_method, "Pickup")
        self.assertEqual(self.order.get_masked_card_number(), "****-****-****-1234")
        self.assertTrue(self.order.tracking_id.startswith("PIZZA-"))

    def test_guest_order_creation(self):
        guest_order = Order.objects.create(
            guest=self.guest,
            name="Guest Customer",
            email="guest@example.com",
            address="456 Guest St",
            city="Raleigh",
            state="NC",
            zip_code="27601",
            phone="555-5678",
            restaurant_location=self.location,
            delivery_method="Delivery"
        )
        self.assertEqual(guest_order.guest, self.guest)
        self.assertEqual(guest_order.name, "Guest Customer")

    def test_order_total_calculation(self):
        # Add pizza to order
        OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=1,
            topping_1=self.topping1,
            topping_2=self.topping2
        )

        # Add wings to order
        OrderWings.objects.create(
            order=self.order,
            wing=self.wings,
            quantity=2
        )

        # Add drink to order
        OrderDrinks.objects.create(
            order=self.order,
            drink=self.drink,
            quantity=1
        )

        # Add dessert to order
        OrderDesserts.objects.create(
            order=self.order,
            dessert=self.dessert,
            quantity=1
        )

        # ✅ Refresh order from DB
        self.order.refresh_from_db()

        # ✅ Force total recalculation to ensure signal latency doesn’t interfere
        self.order.total_price = self.order.calculate_total_price()
        self.order.save(update_fields=["total_price"])

        # Calculate expected total
        pizza_price = Decimal('14.99') + Decimal('1.50') + Decimal('1.00')  # large pizza + 2 toppings
        wings_price = Decimal('8.99') * 2
        drink_price = Decimal('1.99')
        dessert_price = Decimal('4.99')
        expected_total = pizza_price + wings_price + drink_price + dessert_price

        self.assertEqual(self.order.total_price, expected_total)

    def test_order_summary_generation(self):
        # Add items to order
        OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=1,
            topping_1=self.topping1
        )

        OrderWings.objects.create(
            order=self.order,
            wing=self.wings,
            quantity=2
        )

        # Generate summary
        summary = json.loads(self.order.generate_order_summary())

        self.assertEqual(summary['customer_id'], self.user.id)
        self.assertEqual(summary['tracking_id'], self.order.tracking_id)
        self.assertEqual(len(summary['order']['pizzas']), 1)
        self.assertEqual(summary['order']['pizzas'][0]['name'], "Margherita")
        self.assertEqual(summary['order']['pizzas'][0]['toppings'], ["Pepperoni"])
        self.assertEqual(len(summary['order']['wings']), 1)

    def test_restaurant_location_details(self):
        self.assertEqual(self.order.restaurant_address, "123 Main St")
        self.assertEqual(self.order.restaurant_city, "Raleigh")
        self.assertEqual(self.order.restaurant_state, "NC")


class OrderItemTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            phone="555-1234",
            address="123 Main St",
            password="testpass123"
        )

        # Create menu items
        self.pizza = Pizza.objects.create(
            name="Margherita",
            description="Classic margherita pizza",
            price_small=Decimal('10.99'),
            price_medium=Decimal('12.99'),
            price_large=Decimal('14.99')
        )

        self.topping1 = Topping.objects.create(name="Pepperoni", price=Decimal('1.50'))
        self.topping2 = Topping.objects.create(name="Mushrooms", price=Decimal('1.00'))

        self.wings = Wing.objects.create(
            name="Buffalo",
            price=Decimal('8.99'),
            description="Spicy buffalo wings"
        )

        self.drink = Drink.objects.create(
            name="Coke",
            price=Decimal('1.99'),
            description="Regular Coke"
        )

        self.dessert = Dessert.objects.create(
            name="Chocolate Cake",
            price=Decimal('4.99'),
            description="Rich chocolate cake"
        )

        # Create order
        self.order = Order.objects.create(
            customer=self.user,
            address="123 Main St",
            city="Raleigh",
            state="NC",
            zip_code="27601",
            phone="555-1234",
            delivery_method="Pickup"
        )

    def test_pizza_item_creation(self):
        pizza_item = OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=1,
            topping_1=self.topping1,
            topping_2=self.topping2
        )

        expected_price = Decimal('14.99') + Decimal('1.50') + Decimal('1.00')
        self.assertEqual(pizza_item.get_price(), expected_price)

    def test_pizza_item_quantity(self):
        pizza_item = OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=2,
            topping_1=self.topping1
        )

        expected_price = (Decimal('14.99') + Decimal('1.50')) * 2
        self.assertEqual(pizza_item.get_price(), expected_price)

    def test_duplicate_pizza_merging(self):
        # Create first pizza item
        pizza_item1 = OrderPizza.objects.create(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=1,
            topping_1=self.topping1
        )

        # Create identical pizza item
        pizza_item2 = OrderPizza(
            order=self.order,
            pizza=self.pizza,
            size="large",
            quantity=2,
            topping_1=self.topping1
        )
        pizza_item2.save()  # Should merge with pizza_item1

        # Verify merge happened
        pizza_item1.refresh_from_db()
        self.assertEqual(pizza_item1.quantity, 3)
        self.assertEqual(OrderPizza.objects.count(), 1)

    def test_wings_item_creation(self):
        wings_item = OrderWings.objects.create(
            order=self.order,
            wing=self.wings,
            quantity=2
        )

        expected_price = Decimal('8.99') * 2
        self.assertEqual(wings_item.get_price(), expected_price)

    def test_drink_item_creation(self):
        drink_item = OrderDrinks.objects.create(
            order=self.order,
            drink=self.drink,
            quantity=3
        )

        expected_price = Decimal('1.99') * 3
        self.assertEqual(drink_item.get_price(), expected_price)

    def test_dessert_item_creation(self):
        dessert_item = OrderDesserts.objects.create(
            order=self.order,
            dessert=self.dessert,
            quantity=1
        )

        expected_price = Decimal('4.99')
        self.assertEqual(dessert_item.get_price(), expected_price)