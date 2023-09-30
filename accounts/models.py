from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    special_instructions = models.TextField(blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'