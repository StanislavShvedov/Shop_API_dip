from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
import yaml

from .models import Product, ProductCategory, Shop, ShopProduct, Parameters, ProductInfo
from .serializers import (ProductSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer, CreateProductCardSerializer)
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key


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


class ImportProducts(APIView):
    def post(self, request):
        yaml_file = request.FILES.get('yaml_file')
        data = yaml.safe_load(yaml_file.read())
        shop_instance = None
        parameters_instance = None
        for key, values in data.items():

            if key == 'shop':
                try:
                    shop_instance = Shop.objects.create(name=values)
                except Exception as e:
                    return Response({'status': f"Error: {e}"})

            if key == 'categories':
                for category in values:
                    try:
                        ProductCategory.objects.create(id=category['id'], name=category['name'])
                    except Exception as e:
                        return Response({'status': f"Error: {e}"})

            if key == 'goods':
                for product in values:
                    try:
                        print(product['name'])
                        print(translat_text_en_ru(product['name']))
                        category_instance = ProductCategory.objects.get(id=product['category'])
                        product_instance = Product.objects.create(id=product['id'],
                                                                  name=translat_text_en_ru(product['name']),
                                                                  category=category_instance)

                        ShopProduct.objects.create(shop=shop_instance, product=product_instance,
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
                                    if translator_key(key) == "Smart TV":
                                        smart_tv = value
                                    if translator_key(key) == "Capacity (GB)":
                                        capacity = value

                                    parameters_instance = Parameters.objects.create(screen_size=screen_size,
                                                              resolution=resolution,
                                                              internal_memory=internal_memory,
                                                              color=color)

                                elif product_instance.category.name == 'Flash-накопители':

                                    if translator_key(key) == "Screen Size (inches)":
                                        screen_size = value
                                    if translator_key(key) == "Resolution (pixels)":
                                        resolution = value
                                    if translator_key(key) == "Internal Memory (GB)":
                                        internal_memory = value
                                    if translator_key(key) == "Color":
                                        color = value
                                    if translator_key(key) == "Smart TV":
                                        smart_tv = value
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
                                    if translator_key(key) == "Internal Memory (GB)":
                                        internal_memory = value
                                    if translator_key(key) == "Color":
                                        color = value
                                    if translator_key(key) == "Smart TV":
                                        smart_tv = value
                                    if translator_key(key) == "Capacity (GB)":
                                        capacity = value

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
                        return Response({'status': f'Произошла ошибка при импорте продуктов из каталога {yaml_file}: {e}'})
        return Response({'status': f'Продукты из каталога {yaml_file} успешно импортированы'})