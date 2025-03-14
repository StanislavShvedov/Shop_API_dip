import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
import yaml

from .models import Product, ProductCategory, Shop, ShopProduct, Parameters, ProductInfo, Order, OrderProduct
from .permissions import IsOwnerOrReadOnly, IsOwner
from .serializers import (ProductListSerializer, ProductDetailSerializer, ProductCategorySerializer,
                          ShopSerializer, ShopProductSerializer, CreateProductCardSerializer,
                          UserSerializer, ParametersSerializer, OrderSerializer)
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key


# Create your views here.
class ShopViewSet(ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from django.shortcuts import render
from .models import Shop


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
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

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
                            ProductCategory.objects.create(user=user,
                                                           id=category['id'],
                                                           name=category['name'],
                                                           shop=shop_instance)
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

                        info_instance = ProductInfo.objects.create(user=user,
                                                   model=product['model'],
                                                   price=product['price'],
                                                   price_rrc=product['price_rrc'],
                                                   product=product_instance)

                        if product['parameters']:
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
                                capacity=capacity,
                                product_info=info_instance)

                    except Exception as e:
                        if yaml_file:
                            return Response(
                                {'status': f'Произошла ошибка при импорте продуктов из каталога {yaml_file}: {e}'})
                        elif yaml_url:
                            return Response(
                            {'status': f'Произошла ошибка при импорте продуктов из каталога {yaml_url}: {e}'})
        if yaml_file:
            return Response({'status': f'Продукты из каталога {yaml_file} успешно импортированы'})
        elif yaml_url:
            return Response({'status': f'Продукты из каталога {yaml_url} успешно импортированы'})


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
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


def index(request):
    shops = Shop.objects.all()
    templates = 'backend/index.html'
    context = {'shops': shops}
    return render(request, templates, context)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан!')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'backend/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Выводим сообщение об ошибке
            return render(request, 'backend/login.html',
                          {'error': 'Неверное имя пользователя или пароль'})
    else:
        return render(request, 'backend/login.html')


def shop_categories(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    categories = ProductCategory.objects.filter(shop=shop)
    templates = 'backend/shop_categories.html'
    context = {'shop': shop.name, 'categories': categories}
    return render(request, templates, context)


def category_products(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category)
    templates = 'backend/category_products.html'
    context = {'shop': category.shop.name, 'category': category.name, 'products': products, 'shop_id': category.shop.id}
    return render(request, templates, context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    info = ProductInfo.objects.filter(product=product)
    parameters = Parameters.objects.filter(product_info__product=product)
    templates = 'backend/product_detail.html'
    context = {'product': product, 'info': info, 'parameters': parameters, 'category_id': product.category.id}
    return render(request, templates, context)