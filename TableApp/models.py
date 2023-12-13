# models.py
from django.db import models
from django.contrib.auth.models import User

class Register_table(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    loginid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)

class Category(models.Model):
    shop = models.ForeignKey(Register_table, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=255)
    tax = models.DecimalField(max_digits=5, decimal_places=2)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class HomeDelivery(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_received = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)  # New field

    def __str__(self):
        return str(self.user.username)

