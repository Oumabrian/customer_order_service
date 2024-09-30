from django.test import TestCase
from .models import Customer, Order

class CustomerOrderTests(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create(name="John Doe", code="1234")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.code, "1234")
    
    def test_create_order(self):
        customer = Customer.objects.create(name="John Doe", code="1234")
        order = Order.objects.create(customer=customer, item="Laptop", amount=1500)
        self.assertEqual(order.customer.name, "John Doe")
        self.assertEqual(order.item, "Laptop")
        self.assertEqual(order.amount, 1500)
