import requests
from django.db import transaction
from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
import yaml

from .models import Product, ProductCategory, Shop, ShopProduct, Parameters, ProductInfo, Order, OrderProduct
from .permissions import IsOwnerOrReadOnly, IsOwner
from .serializers import (ProductSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer, CreateProductCardSerializer,
                          UserSerializer, ParametersSerializer)
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key


# Create your views here.
class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShopProductViewSet(ModelViewSet):
    queryset = ShopProduct.objects.all()
    serializer_class = ShopProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreateProductCardViewSet(ModelViewSet):
    http_method_names = ['post']
    queryset = Product.objects.all()
    serializer_class = CreateProductCardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'Карточка товара успешно создана'})


@method_decorator(transaction.atomic, name='dispatch')
class ImportProductsView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request):
        yaml_file = request.FILES.get('yaml_file')
        if yaml_file:
            data = yaml.safe_load(yaml_file.read())
        else:
            yaml_url = request.data.get('url')
            try:
                response = requests.get(yaml_url)
                response.raise_for_status()

                data = yaml.safe_load(response.text)
            except Exception as e:
                return Response({'status': f"Error: {e}"})

        shop_instance = None
        parameters_instance = None
        user = User.objects.get(id=request.user.id)

        for key, values in data.items():
            if key == 'shop':
                if Shop.objects.filter(name=values).exists():
                    shop_instance = Shop.objects.get(name=values)
                else:
                    try:
                        shop_instance = Shop.objects.create(user=user, name=values)
                    except Exception as e:
                        return Response({'status': f"Error: {e}"})

            if key == 'categories':
                for category in values:
                    if ProductCategory.objects.filter(name=category['name']).exists():
                        continue
                    else:
                        try:
                            ProductCategory.objects.create(user=user, id=category['id'], name=category['name'])
                        except Exception as e:
                            return Response({'status': f"Error: {e}"})

            if key == 'goods':
                for product in values:
                    if Product.objects.filter(id=product['id']).exists():
                        product_instance = Product.objects.get(id=product['id'])
                        return Response(
                            {'status': f'Товар {product_instance.name} с ID: {product["id"]} уже существует'})
                    try:

                        category_instance = ProductCategory.objects.get(id=product['category'])
                        product_instance = Product.objects.create(user=user,
                                                                  id=product['id'],
                                                                  name=translat_text_en_ru(product['name']),
                                                                  category=category_instance)

                        ShopProduct.objects.create(user=user,
                                                   shop=shop_instance,
                                                   product=product_instance,
                                                   quantity=product['quantity'])

                        if product['parameters']:
                            print(product_instance.name)
                            screen_size = None
                            resolution = None
                            internal_memory = None
                            color = None
                            smart_tv = None
                            capacity = None

                            for key_name, value in product['parameters'].items():
                                if (product_instance.category.name == 'Смартфоны' or
                                        product_instance.category.name == 'Аксессуары'):
                                    if translator_key(key_name) == "Screen Size (inches)":
                                        screen_size = value
                                    if translator_key(key_name) == "Resolution (pixels)":
                                        resolution = value
                                    if translator_key(key_name) == "Internal Memory (GB)":
                                        internal_memory = value
                                    if translator_key(key_name) == "Color":
                                        color = value

                                elif product_instance.category.name == 'Flash-накопители':
                                    if translator_key(key_name) == "Color":
                                        color = value
                                    if translator_key(key_name) == "Capacity (GB)":
                                        capacity = value

                                elif product_instance.category.name == 'Телевизоры':
                                    if translator_key(key_name) == "Screen Size (inches)":
                                        screen_size = value
                                    if translator_key(key_name) == "Resolution (pixels)":
                                        resolution = value
                                    if translator_key(key_name) == "Smart TV":
                                        smart_tv = value

                            parameters_instance = Parameters.objects.create(
                                user=user,
                                screen_size=screen_size,
                                resolution=resolution,
                                internal_memory=internal_memory,
                                color=color,
                                smart_tv=smart_tv,
                                capacity=capacity)
                        print(product['model'], product['price'], product['price_rrc'])
                        ProductInfo.objects.create(user=user,
                                                   model=product['model'],
                                                   price=product['price'],
                                                   price_rrc=product['price_rrc'],
                                                   product=product_instance,
                                                   parameters=parameters_instance)
                    except Exception as e:
                        return Response(
                            {'status': f'Произошла ошибка при импорте продуктов из каталога {yaml_file}: {e}'})
        return Response({'status': f'Продукты из каталога {yaml_file} успешно импортированы'})


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ParamsViewSet(ModelViewSet):
    queryset = Parameters.objects.all()
    serializer_class = ParametersSerializer


class ExportProducts(APIView):
    pass


class OrderViewSet(ModelViewSet):
    pass
