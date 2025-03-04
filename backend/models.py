from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        """Return a string representation of the Shop object using its name."""
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        """Return a string representation of the ProductCategory object using its name."""
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100, null=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category')

    def __str__(self):
        """Return a string representation of the Product object using its name."""
        return self.name


class ShopProduct(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.IntegerField(null=False)


class DynamicField(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)


class Parameters(models.Model):
    screen_size = models.IntegerField(null=True)
    resolution = models.IntegerField(null=True)
    internal_memory = models.IntegerField(null=True)
    color = models.CharField(max_length=50, null=True)
    smart_tv = models.BooleanField(null=True)
    capacity = models.IntegerField(null=True)
    dynamic_fields = models.ManyToManyField(DynamicField)


class ProductInfo(models.Model):
    model = models.CharField(max_length=100, null=False)
    price = models.IntegerField(null=False)
    price_rrc = models.IntegerField(null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)

    def __str__(self):

        return self.model


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(null=False)


class OrderProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
