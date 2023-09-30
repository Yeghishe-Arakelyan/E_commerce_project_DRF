from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .cart import Cart
from shop_m.serializers import ProductSerializer
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .strip_payment import stripe_payment
from .permissions import IsOwner
from django.db import transaction

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsOwner]) 
def add_to_cart(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        product_id = data['id']
        quantity = data.get('quantity', 1)  

        cart = Cart(request)
        success = cart.add_to_cart(product_id, quantity)

        if success:
            return Response({'message': 'Added to your cart'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsOwner])
def view_cart(request):
    cart = Cart(request)
    cart_contents = cart.get_cart_contents()
    total_price = cart.calculate_total_price()

    return Response({'cart': cart_contents, 'total_price': total_price})

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsOwner])
def remove_from_cart(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        product_id = data['id']

        cart = Cart(request)
        cart.remove_from_cart(product_id)

        return Response({'message': 'Item removed from your cart'}, status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner,IsAdminUser]

class OrderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        self.permission_classes = [IsAuthenticated, IsAdminUser]
        self.check_permissions(request)
        return mark_order_as_paid(request, pk)

    @action(detail=True, methods=['post'])
    def mark_as_delivered(self, request, pk=None):
        self.permission_classes = [IsAuthenticated, IsAdminUser]
        self.check_permissions(request)
        return mark_order_as_delivered(request, pk)


def successful_payment_logic(order):
    
    return order.payment_set.filter(successful=True).exists()

def ready_for_delivery_logic(order):
    
    return order.items.filter(ready_for_delivery=True).count() == order.items.count()


@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser])
@transaction.atomic
def mark_order_as_paid(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if order.payment_status != 'paid':
        # Check if a successful payment has been made (you'll need to adapt this logic)
        if successful_payment_logic(order):
            order.payment_status = 'paid'
            order.save()
            return Response({'message': 'Order marked as paid'}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Order payment status remains unchanged'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@transaction.atomic
def mark_order_as_delivered(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if order.delivery_status != 'delivered':
        # Check if the order is ready to be marked as delivered (you'll need to adapt this logic)
        if ready_for_delivery_logic(order):
            order.delivery_status = 'delivered'
            order.save()
            return Response({'message': 'Order marked as delivered'}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Order delivery status remains unchanged'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart = Cart(request)
    order = Order.objects.create(user=request.user)
    for item in cart:
        OrderItem.objects.create(
            order=order, product=item['product'],
            price=item['price'], quantity=item['quantity']
        )
    return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsOwner])
def checkout(request):

    order_id = request.data.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


    total_price = order.calculate_total_cost() 
    
    secret_key = 'your_stripe_secret_key'  # Replace with your actual Stripe secret key
    token = request.data.get('stripe_token')  # Get the Stripe token from the request
    description = f'Payment for Order #{order.id}'  # Customize the description as needed

    payment_id = stripe_payment(secret_key, token, total_price, description)

    if payment_id:
       
        order.is_paid = True
        order.save()

        return Response({'message': 'Payment successful', 'payment_id': payment_id})
    else:
        return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsOwner,IsAdminUser])
def user_orders(request):
    orders = request.user.orders.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)