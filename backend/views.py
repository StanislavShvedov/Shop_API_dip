from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Product, ProductCategory, Shop, ShopProduct, Parameters, ProductInfo
from .serializers import (ProductSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer, CreateProductCardSerializer)


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


class CreateProductCard(ModelViewSet):
    http_method_names = ['post']
    queryset = Product.objects.all()
    serializer_class = CreateProductCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'Карточка товара успешно создана'})