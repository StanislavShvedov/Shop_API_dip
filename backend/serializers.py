from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from .models import (ProductCategory, Product,
                     ProductInfo, Parameters,
                     Shop, ShopProduct, DynamicField,
                     OrderProduct, Order, DeliveryContacts, UserProfile)
from .validators import validate_password


class ShopSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Shop.

        Преобразует данные модели Shop в формат JSON и обратно.
        Включает поля 'user' и 'name', где поле 'user' доступно только для чтения.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Shop): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
                - read_only_fields (list[str]): Список полей, доступных только для чтения.
    """
    class Meta:
        model = Shop
        fields = ['user', 'name']
        read_only_fields = ['user']


class ProductCategorySerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели ProductCategory.

        Преобразует данные модели ProductCategory в формат JSON и обратно.
        Включает поля 'user', 'name' и 'shop', где поле 'user' доступно только для чтения.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (ProductCategory): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
                - read_only_fields (list[str]): Список полей, доступных только для чтения.
    """
    class Meta:
        model = ProductCategory
        fields = ['user', 'name', 'shop']
        read_only_fields = ['user']


class ShopProductSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели ShopProduct.

        Преобразует данные модели ShopProduct в формат JSON и обратно.
        Включает поля 'shop_name', 'product_name' и 'quantity', где 'shop_name' и 'product_name'
        являются только для чтения и отображают связанные имена магазина и продукта.

        Атрибуты:
            - shop_name (ReadOnlyField): Имя магазина, доступное только для чтения.
            - product_name (ReadOnlyField): Имя продукта, доступное только для чтения.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (ShopProduct): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    shop_name = serializers.ReadOnlyField(source='shop.name')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ShopProduct
        fields = ['shop_name', 'product_name', 'quantity']


class DynamicFieldSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели DynamicField.

        Преобразует данные модели DynamicField в формат JSON и обратно.
        Включает поля 'name' и 'value'.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (DynamicField): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    class Meta:
        model = DynamicField
        fields = ['name', 'value']

class ParametersSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Parameters.

        Преобразует данные модели Parameters в формат JSON и обратно.
        Включает поля 'screen_size', 'resolution', 'internal_memory', 'color', 'smart_tv', 'capacity'
        и вложенные динамические поля 'dynamic_fields'.

        Атрибуты:
            - dynamic_fields (DynamicFieldSerializer): Вложенный сериализатор для динамических полей.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Parameters): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.

        Методы:
            - to_representation(instance) -> dict:
                Удаляет из представления поля со значением None.
    """
    dynamic_fields = DynamicFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Parameters
        fields = ['screen_size', 'resolution', 'internal_memory', 'color', 'smart_tv', 'capacity', 'dynamic_fields']

    def to_representation(self, instance) -> dict:
        """
            Аргументы:
                - instance: Экземпляр модели Parameters.

            Возвращает:
                - dict: Представление данных без полей, имеющих значение None.
        """
        representation = super().to_representation(instance)

        for field in list(representation.keys()):
            if representation[field] is None:
                del representation[field]

        return representation


class ProductInfoSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели ProductInfo.

        Преобразует данные модели ProductInfo в формат JSON и обратно.
        Включает поля 'model', 'price', 'price_rrc' и вложенные параметры 'info_parameters'.

        Атрибуты:
            - info_parameters (ParametersSerializer): Вложенный сериализатор для параметров продукта.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (ProductInfo): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    info_parameters = ParametersSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['model', 'price', 'price_rrc', 'info_parameters']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Product (детальное представление).

        Преобразует данные модели Product в формат JSON и обратно.
        Включает поля 'id', 'name', 'category', 'user' и вложенные данные 'product_info'.

        Атрибуты:
            - product_info (ProductInfoSerializer): Вложенный сериализатор для информации о продукте.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Product): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    product_info = ProductInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user', 'product_info']


class ProductListSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Product (списочное представление).

        Преобразует данные модели Product в формат JSON и обратно.
        Включает поля 'id', 'name', 'category', 'user' и 'price'.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Product): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user', 'price']

    def get_price(self, obj):
        """
        Получает значение поля 'price' из первого связанного объекта product_info.

        Args:
            obj (Product): Экземпляр модели Product.

        Returns:
            float or None: Значение поля 'price' или None, если product_info пуст.
        """
        product_info = obj.product_info.first()
        return product_info.price if product_info else None


class ProductSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Product.

        Преобразует данные модели Product в формат JSON и обратно.
        Включает поля 'id', 'name', 'category' и 'user'.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Product): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user']


class CreateProductCardSerializer(serializers.Serializer):
    """
        Сериализатор для создания карточки продукта.

        Позволяет создать связанные объекты: магазин, категорию, продукт, информацию о продукте и параметры.
        Все поля, кроме указанных как required=False, являются обязательными.

        Атрибуты:
            - user (IntegerField): ID пользователя, создающего карточку продукта.
            - shop_name (CharField): Название магазина.
            - category_name (CharField): Название категории продукта.
            - product_name (CharField): Название продукта.
            - quantity (IntegerField): Количество продукта в магазине.
            - model (CharField): Модель продукта.
            - price (IntegerField): Цена продукта.
            - price_rrc (IntegerField): Рекомендуемая розничная цена продукта.
            - screen_size (FloatField): Размер экрана (опционально).
            - resolution (CharField): Разрешение экрана (опционально).
            - internal_memory (IntegerField): Встроенная память (опционально).
            - color (CharField): Цвет продукта (опционально).
            - smart_tv (BooleanField): Признак "Умного" телевизора (опционально).
            - capacity (IntegerField): Ёмкость (опционально).

        Методы:
            - create(validated_data) -> dict:
                Создает связанные объекты на основе валидированных данных.
    """
    user = serializers.IntegerField()
    shop_name = serializers.CharField(max_length=50)
    category_name = serializers.CharField(max_length=50)
    product_name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField()
    model = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    price_rrc = serializers.IntegerField()
    screen_size = serializers.FloatField(required=False)
    resolution = serializers.CharField(required=False)
    internal_memory = serializers.IntegerField(required=False)
    color = serializers.CharField(max_length=50, required=False)
    smart_tv = serializers.BooleanField(required=False)
    capacity = serializers.IntegerField(required=False)

    def create(self, validated_data) -> dict:
        user = User.objects.get(id=validated_data['user'])
        # Создание магазина
        shop_name = validated_data['shop_name']
        shop = Shop.objects.create(user=user, name=shop_name)

        # Создание категории продукта
        category_name = validated_data['category_name']
        category, _ = ProductCategory.objects.get_or_create(user=user, name=category_name, shop=shop)

        # Создание продукта
        product_name = validated_data['product_name']
        product, _ = Product.objects.get_or_create(user=user, name=product_name, category=category)

        # Создание продукта в магазине
        quantity = validated_data['quantity']
        ShopProduct.objects.create(user=user, shop=shop, product=product, quantity=quantity)

        # Создание информации о продукте
        model = validated_data['model']
        price = validated_data['price']
        price_rrc = validated_data['price_rrc']
        screen_size = validated_data['screen_size']
        resolution = validated_data['resolution']
        internal_memory = validated_data['internal_memory']
        color = validated_data['color']
        smart_tv = validated_data['smart_tv']
        capacity = validated_data['capacity']

        product_info, _ = ProductInfo.objects.create(
            user=user,
            model=model,
            price=price,
            price_rrc=price_rrc,
            product=product,
        )

        Parameters.objects.get_or_create(
            user=user,
            screen_size=screen_size,
            resolution=resolution,
            internal_memory=internal_memory,
            color=color,
            smart_tv=smart_tv,
            capacity=capacity,
            product_info=product_info
        )

        return validated_data


class UserSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели User.

        Преобразует данные модели User в формат JSON и обратно.
        Включает поля 'username', 'first_name', 'last_name', 'email' и 'password'.
        Поле 'password' доступно только для записи и проходит валидацию.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (User): Модель, с которой работает сериализатор.
                - fields (tuple[str]): Список полей модели, которые будут сериализованы.
                - extra_kwargs (dict): Дополнительные настройки полей. Поле 'password' доступно только для записи.

        Методы:
            - validate(data) -> dict:
                Проверяет обязательность полей 'username', 'email' и 'password'.

            - validate_password(value) -> str:
                Валидирует пароль с использованием Django-валидаторов.

            - create(validated_data) -> User:
                Создает нового пользователя и устанавливает зашифрованный пароль.

        Сигналы:
            - create_auth_token(sender, instance, created, **kwargs):
                Создает токен аутентификации при создании нового пользователя.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data) -> dict:
        """
            Аргументы:
                - data (dict): Валидируемые данные.

            Возвращает:
                - dict: Валидированные данные.

            Исключения:
                - ValidationError: Если обязательные поля отсутствуют.
        """
        if not data.get('username'):
            raise ValidationError("Имя пользователя обязательно")
        if not data.get('email'):
            raise ValidationError("Электронная почта обязательна")
        if not data.get('password'):
            raise ValidationError("Пароль обязателен")
        return data

    def validate_password(self, value) -> str:
        """
            Аргументы:
                - value (str): Пароль для валидации.

            Возвращает:
                - str: Валидированный пароль.

            Исключения:
                - ValidationError: Если пароль не соответствует требованиям.
        """
        validate_password(value)
        return value

    def create(self, validated_data) -> User:
        """
            Аргументы:
                - validated_data (dict): Валидированные данные пользователя.

            Возвращает:
                - User: Созданный экземпляр пользователя.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    @receiver(post_save, sender=User)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        """
            Аргументы:
                - sender: Класс отправителя сигнала.
                - instance (User): Экземпляр пользователя.
                - created (bool): Флаг, указывающий, был ли объект создан.
                - **kwargs: Дополнительные аргументы.
        """
        if created:
            Token.objects.create(user=instance)


class OrderProductSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели OrderProduct.

        Преобразует данные модели OrderProduct в формат JSON и обратно.
        Включает вложенные сериализаторы для полей 'product' и 'shop_product'.

        Атрибуты:
            - product (ProductSerializer): Вложенный сериализатор для продукта.
            - shop_product (ShopProductSerializer): Вложенный сериализатор для продукта магазина.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (OrderProduct): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
                - read_only_fields (list[str]): Список полей, доступных только для чтения.
    """
    product = ProductSerializer()
    shop_product = ShopProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'shop_product', 'quantity']
        read_only_fields = ['product_info']


class DeliveryContactsSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели DeliveryContacts.

        Преобразует данные модели DeliveryContacts в формат JSON и обратно.
        Включает поля 'city', 'street', 'house_number', 'apartment_number' и 'phone_number'.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (DeliveryContacts): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
    """
    class Meta:
        model = DeliveryContacts
        fields = ['city', 'street', 'house_number', 'apartment_number', 'phone_number']

class OrderSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Order.

        Преобразует данные модели Order в формат JSON и обратно.
        Включает вложенные сериализаторы для полей 'order_products' и 'delivery_contacts'.

        Атрибуты:
            - order_products (OrderProductSerializer): Вложенный сериализатор для товаров в заказе.
            - delivery_contacts (DeliveryContactsSerializer): Вложенный сериализатор для контактных данных доставки.
            - Meta: Внутренний класс для настройки сериализатора.
                - model (Order): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
                - read_only_fields (list[str]): Список полей, доступных только для чтения.
    """
    order_products = OrderProductSerializer(many=True, read_only=True)
    delivery_contacts = DeliveryContactsSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status_choice', 'created_at', 'updated_at',
                  'total_price', 'order_products', 'delivery_choice', 'delivery_contacts']
        read_only_fields = ['user', 'status_choice', 'total_price']


class UserProfileSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели UserProfile.

        Преобразует данные модели UserProfile в формат JSON и обратно.
        Включает поля 'user' и 'phone_number'.

        Атрибуты:
            - Meta: Внутренний класс для настройки сериализатора.
                - model (UserProfile): Модель, с которой работает сериализатор.
                - fields (list[str]): Список полей модели, которые будут сериализованы.
                - read_only_fields (list[str]): Список полей, доступных только для чтения.
    """
    class Meta:
        model = UserProfile
        fields = ['user', 'avatar', 'avatar_thumbnail',]
        read_only_fields = ['user']
