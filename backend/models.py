from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the Shop object using its name."""
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the ProductCategory object using its name."""
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the Product object using its name."""
        return self.name


class ShopProduct(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DynamicField(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)


class Parameters(models.Model):
    screen_size = models.FloatField(null=True, blank=True)
    resolution = models.CharField(max_length=10, null=True, blank=True)
    internal_memory = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    smart_tv = models.BooleanField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    dynamic_fields = models.ManyToManyField(DynamicField)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ProductInfo(models.Model):
    model = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    price_rrc = models.DecimalField(decimal_places=2, max_digits=7)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):

        return self.model


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


