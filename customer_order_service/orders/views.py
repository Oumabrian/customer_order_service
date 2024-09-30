from rest_framework import viewsets
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
import africastalking

# Initialize Africa's Talking with your Sandbox credentials
africastalking.initialize('Sandbox', 'atsk_63dffd5d5d22d876e0516c84c8756cf4845f114a9b3007411bf4fff3ae9eeb00db950a65')

# Function to send SMS using Africa's Talking
def send_sms(customer_phone, message):
    sms = africastalking.SMS
    try:
        # Sending the SMS
        response = sms.send(message, [customer_phone])
        print(f"SMS sent successfully: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

# ViewSet for Customer
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

# ViewSet for Order
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # Override perform_create to send SMS when an order is created
    def perform_create(self, serializer):
        order = serializer.save()  # Save the order instance
        customer = order.customer  # Get the customer related to the order
        
        # Compose the SMS message
        message = f"Hello {customer.name}, your order for {order.item} has been placed successfully."
        
        # Send SMS to the customer's phone number
        send_sms(customer.phone, message)
