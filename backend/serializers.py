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