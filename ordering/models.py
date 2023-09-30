from django.db import models
from django.contrib.auth.models import User
from shop_m.models import Product

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid')],
        default='pending'
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')],
        default='pending'
    )
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"{self.user.first_name} - order id: {self.id}"

    @property
    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    price = models.IntegerField()
    quantity = models.SmallIntegerField(default=1)
    ready_for_delivery = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_status = models.CharField(max_length=20, choices=[('pending', 'Pending'),
                                                               ('shipped', 'Shipped'),
                                                               ('delivered', 'Delivered')],
                                                                default='pending')
    delivery_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id}"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=[('paypal', 'PayPal'), ('card', 'Credit Card')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"