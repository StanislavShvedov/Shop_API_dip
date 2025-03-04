from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Product, ProductCategory, Shop, ShopProduct, Parameters, ProductInfo
from .serializers import (ProductSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer)


# Create your views here.
class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

class ShopProductViewSet(ModelViewSet):
    queryset = ShopProduct.objects.all()
    serializer_class = ShopProductSerializer


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
