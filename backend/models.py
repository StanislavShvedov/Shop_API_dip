from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Shop(models.Model):
    """
        Модель для представления магазина.

        Атрибуты:
            - name (CharField): Название магазина (уникальное, максимальная длина 50 символов).
            - user (ForeignKey): Связь с пользователем, который создал магазин.
                                 При удалении пользователя магазин также удаляется.

        Методы:
            - __str__() -> str:
                Возвращает строковое представление объекта магазина (его название).
    """
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class ProductCategory(models.Model):
    """
        Модель для представления категории продукта.

        Атрибуты:
            - name (CharField): Название категории продукта (максимальная длина 50 символов).
            - user (ForeignKey): Связь с пользователем, который создал категорию.
                                 При удалении пользователя категория также удаляется.
            - shop (ForeignKey): Связь с магазином, к которому относится категория.
                                 При удалении магазина категория также удаляется.
                                 По умолчанию значение не задано (default=None).

        Методы:
            - __str__() -> str:
                Возвращает строковое представление объекта категории (ее название).
    """
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default=None)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """
        Модель для представления продукта.

        Атрибуты:
            - name (CharField): Название продукта (максимальная длина 100 символов).
            - category (ForeignKey): Связь с категорией, к которой относится продукт.
                                     При удалении категории продукт также удаляется.
                                     Используется related_name='category' для обратной связи.
            - is_available (BooleanField): Флаг доступности продукта. По умолчанию True.
            - user (ForeignKey): Связь с пользователем, который создал продукт.
                                 При удалении пользователя продукт также удаляется.

        Методы:
            - __str__() -> str:
                Возвращает строковое представление объекта продукта (его название).
    """
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category')
    is_available = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class ShopProduct(models.Model):
    """
        Модель для представления связи между магазином и продуктом.

        Атрибуты:
            - shop (ForeignKey): Связь с магазином, к которому относится продукт.
                                 При удалении магазина запись также удаляется.
                                 Используется related_name='shop' для обратной связи.
            - product (ForeignKey): Связь с продуктом, который находится в магазине.
                                    При удалении продукта запись также удаляется.
                                    Используется related_name='product' для обратной связи.
            - quantity (IntegerField): Количество продукта в магазине.
            - user (ForeignKey): Связь с пользователем, который создал запись.
                                 При удалении пользователя запись также удаляется.

        Методы:
            не определены
    """
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DynamicField(models.Model):
    """
        Модель для представления динамических полей.

        Атрибуты:
            - name (CharField): Название динамического поля (максимальная длина 100 символов).
            - value (CharField): Значение динамического поля (максимальная длина 255 символов).

        Методы:
            не определены
    """
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)


class ProductInfo(models.Model):
    """
        Модель для представления информации о продукте.

        Атрибуты:
            - model (CharField): Модель продукта (максимальная длина 100 символов).
            - price (DecimalField): Цена продукта с точностью до 2 знаков после запятой.
            - price_rrc (DecimalField): Рекомендованная розничная цена (RRC) продукта с точностью до 2 знаков после запятой.
            - product (ForeignKey): Связь с продуктом, к которому относится информация.
                                    При удалении продукта информация также удаляется.
                                    Используется related_name='product_info' для обратной связи.
            - user (ForeignKey): Связь с пользователем, который создал информацию о продукте.
                                 При удалении пользователя информация также удаляется.

        Методы:
            - __str__() -> str:
                Возвращает строковое представление объекта информации о продукте (его модель).
    """
    model = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    price_rrc = models.DecimalField(decimal_places=2, max_digits=10)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.model

class Parameters(models.Model):
    """
        Модель для представления параметров продукта.

        Атрибуты:
            - screen_size (FloatField): Размер экрана (опционально).
            - resolution (CharField): Разрешение экрана (максимальная длина 10 символов, опционально).
            - internal_memory (IntegerField): Встроенная память (опционально).
            - color (CharField): Цвет продукта (максимальная длина 100 символов, опционально).
            - smart_tv (BooleanField): Признак "Умного" телевизора (опционально).
            - capacity (IntegerField): Ёмкость (опционально).
            - dynamic_fields (ManyToManyField): Связь с динамическими полями.
            - user (ForeignKey): Связь с пользователем, который создал параметры.
                                 При удалении пользователя параметры также удаляются.
                                 Используется related_name='user' для обратной связи.
            - product_info (ForeignKey): Связь с информацией о продукте, к которой относятся параметры.
                                         При удалении информации о продукте параметры также удаляются.
                                         Используется related_name='info_parameters' для обратной связи.

        Методы:
            не определены
        """
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
    """
       Модель для представления связи между заказом и продуктом.

       Атрибуты:
           - product (ForeignKey): Связь с продуктом, который добавлен в заказ.
                                   При удалении продукта запись также удаляется.
                                   Используется related_name='products' для обратной связи.
           - shop_product (ForeignKey): Связь с продуктом магазина, который добавлен в заказ.
                                        При удалении продукта магазина запись также удаляется.
                                        Используется related_name='shop_products' для обратной связи.
           - order (ForeignKey): Связь с заказом, к которому относится продукт.
                                 При удалении заказа запись также удаляется.
                                 Используется related_name='order_products' для обратной связи.
           - quantity (IntegerField): Количество продукта в заказе.

       Методы:
           - update_product_quantity(action: str) -> int:
               Обновляет количество продукта на складе в зависимости от действия ('out_of_stock' или 'in_stock').
               Возвращает обновленное количество продукта на складе.
   """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, related_name='shop_products')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products')
    quantity = models.IntegerField()

    def update_product_quantity(self, action: str):
        """
           Аргументы:
                - action (str): Действие для обновления количества:
                    - 'out_of_stock': Уменьшает количество товара на складе.
                    - 'in_stock': Увеличивает количество товара на складе.

            Возвращает:
                - int: Обновленное количество продукта на складе.

            Исключения:
                - ValueError: Если действие 'out_of_stock' и недостаточно товара на складе.
        """
        if action == 'out_of_stock':
            if self.shop_product.quantity >= self.quantity:
                self.shop_product.quantity -= self.quantity
                self.shop_product.save()
                return self.shop_product.quantity
            else:
                raise ValueError("Недостаточно товара на складе")
        elif action == 'in_stock':
            self.shop_product.quantity += self.quantity
            self.shop_product.save()
            return self.shop_product.quantity


class DeliveryContacts(models.Model):
    """
        Модель для представления контактных данных доставки.

        Атрибуты:
            - city (CharField): Город доставки (максимальная длина 50 символов).
            - street (CharField): Улица доставки (максимальная длина 100 символов).
            - house_number (CharField): Номер дома (максимальная длина 20 символов).
            - apartment_number (CharField): Номер квартиры (максимальная длина 10 символов, опционально).
            - phone_number (CharField): Номер телефона для связи (максимальная длина 11 символов).

        Методы: 
            str: Возвращает строковое представление модели.
    """
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=20)
    apartment_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=11)

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    """
        Модель для представления заказа.

        Атрибуты:
            - ORDER_STATUS_CHOICES (list[tuple[str, str]]): Список возможных статусов заказа.
            - user (ForeignKey): Связь с пользователем, который создал заказ.
                                 При удалении пользователя заказ также удаляется.
            - status_choice (CharField): Текущий статус заказа. По умолчанию 'empty' (Пустой).
            - delivery_choice (BooleanField): Флаг выбора доставки. По умолчанию False.
            - total_price (DecimalField): Общая стоимость заказа с точностью до 2 знаков после запятой.
                                          По умолчанию 0.
            - created_at (DateTimeField): Дата и время создания заказа (автоматически добавляется).
            - updated_at (DateTimeField): Дата и время последнего обновления заказа (автоматически обновляется).
            - delivery_contacts (ForeignKey): Связь с контактными данными доставки.
                                              При удалении данных доставки связь обнуляется.
                                              Опционально (null=True, blank=True).

        Методы:
            - get_product_price() -> Decimal:
                Возвращает цену первого продукта в заказе.

            - update_total_price(price: Optional[Decimal] = None) -> None:
                Обновляет общую стоимость заказа на основе цен и количества продуктов.

            - update_status() -> None:
                Обновляет статус заказа в зависимости от наличия продуктов в заказе.
    """
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
                                          related_name='delivery_contacts', null=True, blank=True)

    def get_product_price(self):
        """
            Возвращает:
                - Decimal: Цена первого продукта в заказе.
        """
        price = ProductInfo.objects.filter(product=self.order_products.first().product).first().price
        return price

    def update_total_price(self, price=None) -> None:
        """
                Аргументы:
                    - price (Optional[Decimal]): Цена продукта (опционально).

                Возвращает:
                    - None
        """
        if not self.order_products.exists():
            self.total_price = 0
        else:
            self.total_price = sum(self.get_product_price() * item.quantity for item in self.order_products.all())
            self.save()

    def update_status(self) -> None:
        """
            Возвращает:
                - None
        """
        if not self.order_products.exists():
            self.status_choice = self.ORDER_STATUS_CHOICES[0][0]
        elif self.order_products.exists():
            self.status_choice = self.ORDER_STATUS_CHOICES[1][0]
        self.save()


class VerificationToken(models.Model):
    """
        Модель для представления токена верификации пользователя.

        Атрибуты:
            - user (OneToOneField): Связь с пользователем, которому принадлежит токен.
                                    При удалении пользователя токен также удаляется.
            - token (CharField): Уникальный токен для верификации пользователя (максимальная длина 255 символов).
            - created_at (DateTimeField): Дата и время создания токена (автоматически добавляется).

        Методы:
            - __str__() -> str:
                Возвращает строковое представление объекта токена.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
            Возвращает:
                - str: Строка в формате "Token for <username>".
        """
        return f"Token for {self.user.username}"
