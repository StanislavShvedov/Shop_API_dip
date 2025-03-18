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


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, related_name='shop_products')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products')
    quantity = models.IntegerField()

    def update_product_quantity(self, action: str):
        if action == 'remove':
            if self.shop_product.quantity >= self.quantity:
                self.shop_product.quantity -= self.quantity
                self.shop_product.save()
                return self.shop_product.quantity
            else:
                raise ValueError("Недостаточно товара на складе")
        elif action == 'add':
            self.shop_product.quantity += self.quantity
            self.shop_product.save()
            return self.shop_product.quantity


class DeliveryContacts(models.Model):
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    apartment_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=11)

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('empty', 'Пустой'),
        ('new', 'Новый'),
        ('making an order', 'Оформление заказа'),
        ('done', 'Завершен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status_choice = models.CharField(default=ORDER_STATUS_CHOICES[0][0])
    delivery_choice = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_contacts = models.ForeignKey(DeliveryContacts, on_delete=models.CASCADE,
                                          related_name='delivery_contacts', default=None)

    def get_product_price(self):
        price = ProductInfo.objects.filter(product=self.order_products.first().product).first().price
        return price

    def update_total_price(self, price=None):
        if not self.order_products.exists():
            self.total_price = 0
        else:
            self.total_price = sum(self.get_product_price() * item.quantity for item in self.order_products.all())
            self.save()

    def update_status(self):
        if not self.order_products.exists():
            self.status_choice = self.ORDER_STATUS_CHOICES[0][0]
        elif self.order_products.exists():
            self.status_choice = self.ORDER_STATUS_CHOICES[1][0]
        self.save()
