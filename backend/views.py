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
from .permissions import IsOwnerOrReadOnly
from .serializers import (ProductSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer, CreateProductCardSerializer,
                          UserSerializer)
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key


# Create your views here.
class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        print(self.request.user)


class ShopProductViewSet(ModelViewSet):
    queryset = ShopProduct.objects.all()
    serializer_class = ShopProductSerializer


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CreateProductCardViewSet(ModelViewSet):
    http_method_names = ['post']
    queryset = Product.objects.all()
    serializer_class = CreateProductCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'Карточка товара успешно создана'})

@method_decorator(transaction.atomic, name='dispatch')
class ImportProductsView(APIView):
    def post(self, request):
        yaml_file = request.FILES.get('yaml_file')
        data = yaml.safe_load(yaml_file.read())
        shop_instance = None
        parameters_instance = None
        for key, values in data.items():

            if key == 'shop':
                if Shop.objects.filter(name=values).exists():
                    shop_instance = Shop.objects.get(name=values)
                else:
                    try:
                        shop_instance = Shop.objects.create(name=values)
                    except Exception as e:
                        return Response({'status': f"Error: {e}"})

            if key == 'categories':
                for category in values:
                    if ProductCategory.objects.filter(name=category['name']).exists():
                        continue
                    else:
                        try:
                            ProductCategory.objects.create(id=category['id'], name=category['name'])
                        except Exception as e:
                            return Response({'status': f"Error: {e}"})

            if key == 'goods':
                for product in values:
                    if Product.objects.filter(id=product['id']).exists():
                        product_instance = Product.objects.get(id=product['id'])
                        return Response({'status': f'Товар {product_instance.name} с ID: {product["id"]} уже существует'})
                    try:

                        category_instance = ProductCategory.objects.get(id=product['category'])
                        product_instance = Product.objects.create(id=product['id'],
                                                                  name=translat_text_en_ru(product['name']),
                                                                  category=category_instance)

                        ShopProduct.objects.create(shop=shop_instance,
                                                   product=product_instance,
                                                   quantity=product['quantity'])

                        if product['parameters']:
                            for key, value in product['parameters'].items():
                                screen_size = None
                                resolution = None
                                internal_memory = None
                                color = None
                                smart_tv = None
                                capacity = None

                                if (product_instance.category.name == 'Смартфоны' or
                                        product_instance.category.name == 'Аксессуары'):

                                    if translator_key(key) == "Screen Size (inches)":
                                        screen_size = value
                                    if translator_key(key) == "Resolution (pixels)":
                                        resolution = value
                                    if translator_key(key) == "Internal Memory (GB)":
                                        internal_memory = value
                                    if translator_key(key) == "Color":
                                        color = value

                                    parameters_instance = Parameters.objects.create(screen_size=screen_size,
                                                                                    resolution=resolution,
                                                                                    internal_memory=internal_memory,
                                                                                    color=color)

                                elif product_instance.category.name == 'Flash-накопители':

                                    if translator_key(key) == "Color":
                                        color = value
                                    if translator_key(key) == "Capacity (GB)":
                                        capacity = value

                                    parameters_instance = Parameters.objects.create(
                                        color=color,
                                        capacity=capacity)

                                elif product_instance.category.name == 'Телевизоры':

                                    if translator_key(key) == "Screen Size (inches)":
                                        screen_size = value
                                    if translator_key(key) == "Resolution (pixels)":
                                        resolution = value
                                    if translator_key(key) == "Smart TV":
                                        smart_tv = value

                                    parameters_instance = Parameters.objects.create(
                                        screen_size=screen_size,
                                        resolution=resolution,
                                        smart_tv=smart_tv)

                        ProductInfo.objects.create(model=product['model'],
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


class ExportProducts(APIView):
    pass


class OrderViewSet(ModelViewSet):
    pass

