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
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None)

    def __str__(self):
        """Return a string representation of the ProductCategory object using its name."""
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category')
    is_available = models.BooleanField(default=True)
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


class ProductInfo(models.Model):
    model = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    price_rrc = models.DecimalField(decimal_places=2, max_digits=10)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):

        return self.model

class Parameters(models.Model):
    screen_size = models.FloatField(null=True, blank=True)
    resolution = models.CharField(max_length=10, null=True, blank=True)
    internal_memory = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    smart_tv = models.BooleanField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    dynamic_fields = models.ManyToManyField(DynamicField)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='info_parameters')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_total_price(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.order_products.all())
        self.save()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
