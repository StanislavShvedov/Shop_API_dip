from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import (ProductCategory, Product,
                     ProductInfo, Parameters,
                     Shop, ShopProduct, DynamicField,
                     OrderProduct, Order, DeliveryContacts)
from .validators import validate_password


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['user', 'name']
        read_only_fields = ['user']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['user', 'name', 'shop']
        read_only_fields = ['user']


class ShopProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.ReadOnlyField(source='shop.name')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = ShopProduct
        fields = ['shop_name', 'product_name', 'quantity']


class DynamicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicField
        fields = ['name', 'value']

class ParametersSerializer(serializers.ModelSerializer):
    dynamic_fields = DynamicFieldSerializer(many=True, read_only=True)

    class Meta:
        model = Parameters
        fields = ['screen_size', 'resolution', 'internal_memory', 'color', 'smart_tv', 'capacity', 'dynamic_fields']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        for field in list(representation.keys()):
            if representation[field] is None:
                del representation[field]

        return representation


class ProductInfoSerializer(serializers.ModelSerializer):
    info_parameters = ParametersSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['model', 'price', 'price_rrc', 'info_parameters']


class ProductDetailSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user', 'product_info']


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'user']


class CreateProductCardSerializer(serializers.Serializer):
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

    def create(self, validated_data):
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
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if not data.get('username'):
            raise ValidationError("Имя пользователя обязательно")
        if not data.get('email'):
            raise ValidationError("Электронная почта обязательна")
        if not data.get('password'):
            raise ValidationError("Пароль обязателен")
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    @receiver(post_save, sender=User)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    shop_product = ShopProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'shop_product', 'quantity']
        read_only_fields = ['product_info']


class DeliveryContacts(serializers.ModelSerializer):
    class Meta:
        model = DeliveryContacts
        fields = ['city', 'street', 'house_number', 'apartment_number', 'phone_number']

class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)
    delivery_contacts = DeliveryContacts()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status_choice', 'created_at', 'updated_at',
                  'total_price', 'order_products', 'delivery_choice', 'delivery_contacts']
        read_only_fields = ['user']
