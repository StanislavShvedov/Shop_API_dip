from rest_framework import serializers

from .models import (ProductCategory, Product,
                     ProductInfo, Parameters,
                     Shop, ShopProduct)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category']


class ShopProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.ReadOnlyField(source='shop.name')
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model = ShopProduct
        fields = ['shop_name', 'product_name', 'quantity']

class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['model', 'price', 'price_rrc', 'product_id.name']


class ParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameters
        fields = ['screen_size', 'resolution', 'internal_memory', 'color', 'smart_tv', 'capacity']

class CreateProductCardSerializer(serializers.Serializer):
    shop_name = serializers.CharField(max_length=50)
    category_name = serializers.CharField(max_length=50)
    product_name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField()
    model = serializers.CharField(max_length=100)
    price = serializers.IntegerField()
    price_rrc = serializers.IntegerField()
    screen_size = serializers.IntegerField(required=False)
    resolution = serializers.IntegerField(required=False)
    internal_memory = serializers.IntegerField(required=False)
    color = serializers.CharField(max_length=50, required=False)
    smart_tv = serializers.BooleanField(required=False)
    capacity = serializers.IntegerField(required=False)

    def create(self, validated_data):
        # Создание магазина
        shop_name = validated_data['shop_name']
        print(shop_name)
        shop = Shop.objects.create(name=shop_name)

        # Создание категории продукта
        category_name = validated_data['category_name']
        category, _ = ProductCategory.objects.get_or_create(name=category_name)

        # Создание продукта
        product_name = validated_data['product_name']
        product, _ = Product.objects.get_or_create(name=product_name, category=category)

        # Создание продукта в магазине
        quantity = validated_data['quantity']
        ShopProduct.objects.create(shop=shop, product=product, quantity=quantity)

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

        parameters, _ = Parameters.objects.get_or_create(
            screen_size=screen_size,
            resolution=resolution,
            internal_memory=internal_memory,
            color=color,
            smart_tv=smart_tv,
            capacity=capacity
        )

        ProductInfo.objects.create(
            model=model,
            price=price,
            price_rrc=price_rrc,
            product=product,
            parameters=parameters
        )

        return validated_data
