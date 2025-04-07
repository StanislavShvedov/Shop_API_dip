import uuid
from typing import Any, Type
import requests

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.views import LogoutView
from django.db.models import OuterRef, Subquery

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter


import yaml

from .models import (
    Product,
    ProductCategory,
    Shop,
    ShopProduct,
    Parameters,
    ProductInfo,
    Order,
    OrderProduct,
    VerificationToken,
)
from .permissions import IsOwnerOrReadOnly, IsOwner
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCategorySerializer,
    ShopSerializer,
    ShopProductSerializer,
    CreateProductCardSerializer,
    UserSerializer,
    ParametersSerializer,
    OrderSerializer,
    DeliveryContacts,
)
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key
from .send_email import smtp_user, smtp_password, send_varif_mail
from .tasks import import_products_task


# Create your views here.
class ShopViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели Shop.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для магазинов (Shop). Доступ к операциям редактирования и удаления предоставляется
    только владельцу магазина (IsOwnerOrReadOnly).

    Атрибуты:
        - queryset (QuerySet[Shop]): Набор всех объектов модели Shop.
        - serializer_class (type[ShopSerializer]): Сериализатор для преобразования данных модели Shop.
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используется IsOwnerOrReadOnly для ограничения прав доступа.

    Методы:
        - perform_create(serializer: ShopSerializer) -> None:
            Переопределённый метод для сохранения нового объекта Shop.
            Автоматически присваивает текущего пользователя (request.user) как владельца магазина.
    """

    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]

    def perform_create(self, serializer) -> None:
        """
        Аргументы:
            - serializer (ShopSerializer): Экземпляр сериализатора для валидации и сохранения данных.

        Возвращает:
            - None
        """
        serializer.save(user=self.request.user)


class ShopProductViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели ShopProduct.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для товаров магазина (ShopProduct). Доступ к операциям редактирования и удаления
    предоставляется только владельцу товара (IsOwnerOrReadOnly).

    Атрибуты:
        - queryset (QuerySet[ShopProduct]): Набор всех объектов модели ShopProduct.
        - serializer_class (type[ShopProductSerializer]): Сериализатор для преобразования данных модели ShopProduct.
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используется IsOwnerOrReadOnly для ограничения прав доступа.

    Методы:
        - perform_create(serializer: ShopProductSerializer) -> None:
            Переопределённый метод для сохранения нового объекта ShopProduct.
            Автоматически присваивает текущего пользователя (request.user) как владельца товара.
    """

    queryset = ShopProduct.objects.all()
    serializer_class = ShopProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["shop"]
    search_fields = ["product"]
    ordering_fields = ["quantity"]

    def perform_create(self, serializer) -> None:
        """
        Аргументы:
            - serializer (ShopProductSerializer): Экземпляр сериализатора для валидации и сохранения данных.

        Возвращает:
            - None
        """
        serializer.save(user=self.request.user)


class ProductCategoryViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели ProductCategory.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для категорий товаров (ProductCategory).

    Атрибуты:
        - queryset (QuerySet[ProductCategory]): Набор всех объектов модели ProductCategory.
        - serializer_class (type[ProductCategorySerializer]): Сериализатор для преобразования данных модели
         ProductCategory.
    """

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["name", "shop"]
    search_fields = ["name"]


class ProductsViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели Product.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для товаров (Product). Доступ к операциям редактирования и удаления предоставляется
    только владельцу товара (IsOwnerOrReadOnly).

    Атрибуты:
        - queryset (QuerySet[Product]): Набор всех объектов модели Product.
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используется IsOwnerOrReadOnly для ограничения прав доступа.

    Методы:
        - get_serializer_class() -> Type[Serializer]:
            Переопределённый метод для выбора сериализатора в зависимости от действия.
            Для действия 'retrieve' используется ProductDetailSerializer, для остальных действий — ProductListSerializer.

        - perform_create(serializer: Serializer) -> None:
            Переопределённый метод для сохранения нового объекта Product.
            Автоматически присваивает текущего пользователя (request.user) как владельца товара.

        - disable_product(request: Request) -> Response:
            Переопределённый метод для отключения товара.
            Проверяет права доступа и возвращает ответ с сообщением об успешном изменении состояния.
            Если товар иктивен, деактивирует его для продажи и наоборот.

        - get_queryset() -> queryset:
            Переопределённый метод для получения queryset объектов Product с аннотированным полем 'price'
    """

    queryset = Product.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "price"]

    def get_serializer_class(self) -> Type[Serializer]:
        """
        Возвращает:
            - Type[Serializer]: Класс сериализатора, соответствующий выполняемому действию.
        """
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        """
        Аргументы:
            - serializer (Serializer): Экземпляр сериализатора для валидации и сохранения данных.

        Возвращает:
            - None
        """
        serializer.save(user=self.request.user)

    def get_queryset(self) -> queryset:
        """
        Returns:
            queryset: QuerySet объектов Product с аннотированным полем 'price'.
        """
        price_subquery = ProductInfo.objects.filter(product=OuterRef("pk")).values(
            "price"
        )[:1]

        queryset = Product.objects.annotate(price=Subquery(price_subquery))

        ordering = self.request.query_params.get("ordering")
        if ordering in ["price", "-price"]:
            queryset = queryset.order_by(ordering)

        return queryset

    @action(detail=False, methods=["post"])
    def disable_enabled_product(self, request):
        """
        Возвращает:
        - При успешном выполнении: JSON-ответ с сообщением об успешном изменении состояния.
        - При отсутствии прав доступа: JSON-ответ с сообщением об ошибке и статусом 403.

        Параметры запроса:
        - product_id (int): Идентификатор продукта, который необходимо отключить/включить.
        """
        if request.user.is_staff or request.user.is_superuser:
            product_id = request.data.get("product_id")
            product = Product.objects.filter(pk=product_id).first()
            if product.is_available:
                product.is_available = False
                product.save()
                return Response({"message": "Product disabled successfully."})
            elif not product.is_available:
                product.is_available = True
                product.save()
                return Response({"message": "Product enabled successfully."})

        return Response(
            {"message": "You do not have permission to disable products."},
            status=status.HTTP_403_FORBIDDEN,
        )


class CreateProductCardViewSet(ModelViewSet):
    """
    ViewSet для создания карточек товаров (Product).

    Поддерживает только HTTP-метод POST.
    Доступ к созданию предоставляется только аутентифицированным пользователям (IsAuthenticated),
    а также владельцам товара (IsOwnerOrReadOnly).

    Атрибуты:
        - http_method_names (list[str]): Список поддерживаемых HTTP-методов.
        - queryset (QuerySet[Product]): Набор всех объектов модели Product.
        - serializer_class (type[CreateProductCardSerializer]): Сериализатор для преобразования данных модели Product.
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используются IsAuthenticated и IsOwnerOrReadOnly.

    Методы:
        - perform_create(serializer: CreateProductCardSerializer) -> None:
            Переопределённый метод для сохранения нового объекта Product.
            Автоматически присваивает текущего пользователя (request.user) как владельца товара.

        - create(request: Request, *args: Any, **kwargs: Any) -> Response:
            Переопределённый метод для обработки запроса на создание карточки товара.
            Валидирует данные, сохраняет объект и возвращает ответ с сообщением об успешном создании.
    """

    http_method_names = ["post"]
    queryset = Product.objects.all()
    serializer_class = CreateProductCardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer) -> None:
        """
        Аргументы:
            - serializer (CreateProductCardSerializer): Экземпляр сериализатора для валидации и сохранения данных.

        Возвращает:
            - None
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs) -> Response:
        """
        Аргументы:
            - request (Request): Объект запроса, содержащий данные для создания карточки товара.
            - *args (Any): Дополнительные позиционные аргументы.
            - **kwargs (Any): Дополнительные именованные аргументы.

        Возвращает:
            - Response: Ответ с сообщением об успешном создании карточки товара.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"status": "Карточка товара успешно создана"})


@method_decorator(transaction.atomic, name="dispatch")
class ImportProductsView(APIView):
    """
    View для импорта товаров из YAML-файла или URL.

    Поддерживает только POST-запросы. Импорт может быть выполнен только
    администраторами или суперпользователями (IsOwner + IsAuthenticated).

    Атрибуты:
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используются IsAuthenticated и IsOwner.

    Методы:
        - perform_create(serializer: Serializer) -> None:
            Переопределённый метод для сохранения объектов с привязкой к текущему пользователю.
            Этот метод используется в других частях кода, но не вызывается напрямую в этом классе.

        - post(request: Request) -> Response:
            Обрабатывает POST-запрос для импорта товаров из YAML-файла или URL.
            Производит проверку прав доступа, загрузку данных, их обработку и сохранение в базу данных.
            import_products_task(data, user) вызывает задачу Celery для асинхронного импорта товаров.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    def post(self, request) -> Response:
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"status": "У вас нет прав для импорта товаров"})
        yaml_file = request.FILES.get("yaml_file")

        try:
            if yaml_file:
                data = yaml.safe_load(yaml_file.read())
            else:
                yaml_url = request.data.get("url")
                try:
                    response = requests.get(yaml_url)
                    response.raise_for_status()

                    data = yaml.safe_load(response.text)
                except Exception as e:
                    return Response({"status": f"Error: {e}"})
            user = User.objects.get(id=request.user.id)
            import_products_task(data, user)
            return Response({"status": "Задача импорта отправлена на выполнение"})

        except Exception as e:
            return Response({"status": f"Ошибка при обработке запроса: {e}"})

        # if yaml_file:
        #     return Response(
        #         {"status": f"Продукты из каталога {yaml_file} успешно импортированы"}
        #     )
        # elif yaml_url:
        #     return Response(
        #         {"status": f"Продукты из каталога {yaml_url} успешно импортированы"}
        #     )


class UserViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели User.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для пользователей (User). Доступ к операциям предоставляется всем пользователям
    без ограничений (AllowAny).

    Атрибуты:
        - queryset (QuerySet[User]): Набор всех объектов модели User.
        - serializer_class (type[UserSerializer]): Сериализатор для преобразования данных модели User.
        - permission_classes (tuple[type[BasePermission], ...]): Кортеж классов разрешений.
          В данном случае используется AllowAny для предоставления доступа всем пользователям.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParamsViewSet(ModelViewSet):
    """
    ViewSet для управления объектами модели Parameters.

    Позволяет выполнять CRUD-операции (создание, чтение, обновление, удаление)
    для параметров товаров (Parameters).

    Атрибуты:
        - queryset (QuerySet[Parameters]): Набор всех объектов модели Parameters.
        - serializer_class (type[ParametersSerializer]): Сериализатор для преобразования данных модели Parameters.
    """

    queryset = Parameters.objects.all()
    serializer_class = ParametersSerializer


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя с дополнительными полями.

    Расширяет стандартную форму UserCreationForm, добавляя поля email и is_staff.
    Проверяет уникальность email и username. Автоматически сохраняет данные пользователя
    в базу данных при вызове метода save().

    Атрибуты:
        - email (EmailField): Поле для ввода email пользователя.
        - is_stuff (BooleanField): Флажок для указания, является ли пользователь поставщиком (staff).
                                   По умолчанию необязательное поле.

    Методы:
        - clean_email() -> str:
            Проверяет уникальность email. Если email уже используется, вызывает ValidationError.

        - clean_username() -> str:
            Проверяет уникальность username. Если имя пользователя уже занято, вызывает ValidationError.

        - save(commit: bool = True) -> User:
            Сохраняет нового пользователя в базу данных. Устанавливает значения email и is_staff.
    """

    email = forms.EmailField(label="Email")
    is_stuff = forms.BooleanField(label="Stuff", required=False)

    class Meta(UserCreationForm.Meta):
        """
        Внутренний класс Meta для настройки формы.

        Атрибуты:
            - fields (tuple[str]): Список полей, которые будут отображаться в форме.
                                   Включает поля из родительского класса и дополнительные поля email и is_stuff.
            - widgets (dict[str, Widget]): Настройка виджетов для полей формы.
                                           Для паролей используется PasswordInput.
        """

        fields = UserCreationForm.Meta.fields + ("email", "is_stuff")
        widgets = {
            "password1": forms.PasswordInput(),
            "password2": forms.PasswordInput(),
        }

    def clean_email(self) -> str:
        """
        Возвращает:
            - str: Проверенный email.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется.")
        return email

    def clean_username(self) -> str:
        """
        Возвращает:
            - str: Проверенное имя пользователя.
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Это имя пользователя уже занято.")
        return username

    def save(self, commit=True) -> User:
        """
        Аргументы:
            - commit (bool): Флаг, указывающий, нужно ли сохранять объект в базу данных.
                             По умолчанию True.

        Возвращает:
            - User: Созданный экземпляр пользователя.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = self.cleaned_data["is_stuff"]
        if commit:
            user.save()
        return user


class OrderViewSet(ModelViewSet):
    """
    ViewSet для управления заказами (Order).

    Позволяет выполнять CRUD-операции с заказами, а также добавлять товары,
    удалять товары и завершать заказы. Доступ к операциям предоставляется только
    аутентифицированным пользователям (IsAuthenticated) и владельцам заказов (IsOwner).

    Атрибуты:
        - serializer_class (type[OrderSerializer]): Сериализатор для преобразования данных модели Order.
        - permission_classes (list[type[BasePermission]]): Список классов разрешений.
          В данном случае используются IsAuthenticated и IsOwner.

    Методы:
        - get_queryset() -> QuerySet[Order]:
            Возвращает набор заказов в зависимости от роли пользователя:
            - Для суперпользователя: все заказы.
            - Для поставщика: заказы, связанные с товарами, которые они создали.
            - Для обычных пользователей: только их собственные заказы.

        - create(request: Request, *args: Any, **kwargs: Any) -> Response:
            Создает новый заказ или возвращает существующий заказ пользователя.

        - add_product(request: Request) -> Response:
            Добавляет товар в заказ пользователя. Если заказа еще не создан, создает его.
            Подсчитывает общую стоимость заказа.
            Убавляет количество товара на складе на велечину, указанную в заказе.

        - delete_product(request: Request) -> Response:
            Удаляет или уменьшает количество товара в заказе пользователя.
            Возвращает товар на склад при удалении из заказа.

        - place_an_order(request: Request) -> Response:
            Завершает заказ, обновляет статус и отправляет письмо подтверждения.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Возвращает:
            - QuerySet[Order]: Набор заказов, доступных пользователю.
        """
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.is_staff:
            return Order.objects.filter(orderitem__product__user=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Аргументы:
            - request (Request): Объект запроса, содержащий данные пользователя.
            - *args (Any): Дополнительные позиционные аргументы.
            - **kwargs (Any): Дополнительные именованные аргументы.

        Возвращает:
            - Response: Ответ сервера с данными о заказе.
        """
        try:
            order = Order.objects.get(user=self.request.user)
        except Order.DoesNotExist or order.ORDER_STATUS_CHOICES == "done":
            order = Order.objects.create(user=self.request.user)
            order.update_total_price()
            order.update_status()
            return Response(
                {
                    "status": f"Заказ успешно создан. Статус: {order.status_choice}. "
                    f"Общая сумма заказа {order.total_price} рублей"
                }
            )
        else:
            return Response(
                {
                    "status": f"Заказ уже создан. Статус: {order.status_choice}. "
                    f"Общая сумма заказа {order.total_price} рублей"
                }
            )

    @action(methods=["post"], detail=False)
    def add_product(self, request):
        """
        Аргументы:
            - request (Request): Объект запроса, содержащий ID товара и его количество.

        Возвращает:
            - Response: Ответ сервера с результатом операции.
        """
        try:
            order = Order.objects.get(
                user=self.request.user.id, status_choice__in=["empty", "new"]
            )
        except Order.DoesNotExist:
            order = Order.objects.create(user=self.request.user)
            order.update_total_price()
            order.update_status()
        if order.status_choice == "new" or order.status_choice == "empty":
            product_id = request.data.get("product_id")
            try:
                product = Product.objects.get(id=product_id)
                if not product.is_available:
                    return Response(
                        {"status": "Товар недоступен для продажи"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Product.DoesNotExist:
                return Response(
                    {"status": "Товар не найден"}, status=status.HTTP_400_BAD_REQUEST
                )
            shop_product = ShopProduct.objects.get(product=product)
            order_quantity = request.data.get("quantity")

            existing_order_product = OrderProduct.objects.filter(
                product=product, order=order
            ).first()
            if existing_order_product:
                try:
                    existing_order_product.quantity += order_quantity
                    existing_order_product.update_product_quantity("out_of_stock")
                    existing_order_product.save()
                except ValueError as e:
                    return Response(
                        {"status": f"{e}"}, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                order_product = OrderProduct.objects.create(
                    product=product,
                    shop_product=shop_product,
                    order=order,
                    quantity=order_quantity,
                )
                try:
                    order_product.update_product_quantity("out_of_stock")
                except ValueError as e:
                    return Response(
                        {"status": f"{e}"}, status=status.HTTP_400_BAD_REQUEST
                    )

            order.update_total_price()
            order.update_status()
            return Response(
                {
                    "status": f"Товар {product.name} успешно добавлен в заказ. Статус: {order.status_choice}. "
                    f"Общая сумма заказа {order.total_price} рублей"
                }
            )
        else:
            return Response(
                {
                    "status": f"Заказ уже завершен. Статус: {order.status_choice}. "
                    f"Общая сумма заказа {order.total_price} рублей"
                }
            )

    @action(methods=["post"], detail=False)
    def delete_product(self, request):
        """
        Аргументы:
            - request (Request): Объект запроса, содержащий ID товара и его количество.

        Возвращает:
            - Response: Ответ сервера с результатом операции.
        """
        try:
            order = Order.objects.get(user=self.request.user.id, status_choice="new")
            product_id = request.data.get("product_id")
            product = Product.objects.get(id=product_id)
            order_product = OrderProduct.objects.filter(
                product=product, order=order
            ).first()
            if not order_product:
                return Response({"status": "Продукт не найден в заказе"})
            order_quantity = request.data.get("quantity")
            if order_product.quantity > order_quantity:
                order_product.quantity -= order_quantity
                order_product.save()
                order_product.update_product_quantity("in_stock")
                order.update_total_price()
                return Response(
                    {
                        "status": f"Заказ обновлен. Статус: {order.status_choice}. "
                        f"Общая сумма заказа {order.total_price} рублей"
                    }
                )
            elif order_product.quantity == order_quantity:
                order_product.delete()
                order_product.update_product_quantity("in_stock")
                order.update_total_price()
                order.update_status()
                return Response(
                    {
                        "status": f"Продукт {product.name} удален из заказа. Статус: {order.status_choice}. "
                        f"Общая сумма заказа {order.total_price} рублей"
                    }
                )
            else:
                return Response(
                    {
                        "status": "Количнство продуктов в заказе меньше указанного количества"
                    }
                )
        except Order.DoesNotExist:
            return Response(
                {"status": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["post"], detail=False)
    def place_an_order(self, request):
        """
        Аргументы:
            - request (Request): Объект запроса, содержащий данные о доставке.

        Возвращает:
            - Response: Ответ сервера с результатом операции.
        """
        delivery_choice = request.data.get("delivery_choice")
        try:
            order = Order.objects.get(user=self.request.user.id, status_choice="new")
            order_product = OrderProduct.objects.filter(order=order)
            if not delivery_choice:
                order.status_choice = "done"
                order.save()

                try:
                    staff_user_id = (
                        OrderProduct.objects.filter(order=order)
                        .first()
                        .shop_product.product.user.id
                    )
                    staff_user_email = User.objects.get(id=staff_user_id).email
                    print(staff_user_email)
                    email_text = (
                        f"Поступил новый заказ.\n"
                        f"'Продукты: {' '.join([item.product.name for item in order_product])}\n"
                        f"Общая сумма заказа {order.total_price} рублей.\n"
                        f"Способ получения - самовывоз "
                    )
                    print(email_text)
                    subj_text = "Новый заказ"
                    send_varif_mail(
                        host_email=smtp_user,
                        password=smtp_password,
                        user_email=staff_user_email,
                        subj_tex=subj_text,
                        mail_text=email_text,
                    )
                except Exception as e:
                    print(f"Ошибка при отправке письма: {str(e)}")
                    messages.error(request, f"Ошибка при отправке письма: {str(e)}")

                try:
                    email_text = (
                        f"Поступил новый заказ.\n"
                        f"'Продукты: {' '.join([item.product.name for item in order_product])}\n"
                        f"Общая сумма заказа {order.total_price} рублей.\n"
                        f"Способ получения - самовывоз "
                    )
                    print(email_text)
                    subj_text = "Подтверждение заказа"
                    send_varif_mail(
                        host_email=smtp_user,
                        password=smtp_password,
                        user_email=order.user.email,
                        subj_tex=subj_text,
                        mail_text=email_text,
                    )
                except Exception as e:
                    print(f"Ошибка при отправке письма: {str(e)}")
                    messages.error(request, f"Ошибка при отправке письма: {str(e)}")

                return Response(
                    {
                        "status": f"Заказ успешно завершен. Статус: {order.status_choice}. "
                        f"Общая сумма заказа {order.total_price} рублей"
                    }
                )
            elif delivery_choice:
                required_fields = [
                    "city",
                    "street",
                    "house_number",
                    "apartment_number",
                    "phone_number",
                ]
                missing_fields = [
                    field for field in required_fields if not request.data.get(field)
                ]

                if missing_fields:
                    return Response(
                        {
                            "status": f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                order.delivery_choice = True
                city = request.data.get("city")
                street = request.data.get("street")
                house_number = request.data.get("house_number")
                apartment_number = request.data.get("apartment_number")
                phone_number = request.data.get("phone_number")
                delivery_contacts = DeliveryContacts.objects.create(
                    city=city,
                    street=street,
                    house_number=house_number,
                    apartment_number=apartment_number,
                    phone_number=phone_number,
                )
                order.delivery_contacts = delivery_contacts
                order.status_choice = "done"
                order.save()

                try:
                    staff_user_id = (
                        OrderProduct.objects.filter(order=order)
                        .first()
                        .shop_product.product.user.id
                    )
                    staff_user_email = User.objects.get(id=staff_user_id).email
                    print(staff_user_email)
                    email_text = (
                        f"Поступил новый заказ.\n"
                        f"'Продукты: {' '.join([item.product.name for item in order_product])}\n"
                        f"Общая сумма заказа {order.total_price} рублей.\n"
                        f"Доставка указана по адресу: город {order.delivery_contacts.city}, "
                        f"улица {order.delivery_contacts.street}, "
                        f"дом {order.delivery_contacts.house_number}, "
                        f"квартира {order.delivery_contacts.apartment_number}."
                    )
                    print(email_text)
                    subj_text = "Новый заказ"
                    send_varif_mail(
                        host_email=smtp_user,
                        password=smtp_password,
                        user_email=staff_user_email,
                        subj_tex=subj_text,
                        mail_text=email_text,
                    )
                except Exception as e:
                    print(f"Ошибка при отправке письма: {str(e)}")
                    messages.error(request, f"Ошибка при отправке письма: {str(e)}")

                try:
                    email_text = (
                        f"Поступил новый заказ. \n"
                        f"'Продукты: {' '.join([item.product.name for item in order_product])}\n"
                        f"Общая сумма заказа {order.total_price} рублей.\n"
                        f"Доставка указана по адресу: город {order.delivery_contacts.city}, "
                        f"улица {order.delivery_contacts.street}, "
                        f"дом {order.delivery_contacts.house_number}, "
                        f"квартира {order.delivery_contacts.apartment_number}."
                    )
                    print(email_text)
                    subj_text = "Подтверждение заказа"
                    send_varif_mail(
                        host_email=smtp_user,
                        password=smtp_password,
                        user_email=order.user.email,
                        subj_tex=subj_text,
                        mail_text=email_text,
                    )
                except Exception as e:
                    print(f"Ошибка при отправке письма: {str(e)}")
                    messages.error(request, f"Ошибка при отправке письма: {str(e)}")

                return Response(
                    {
                        "status": f"Заказ успешно завершен. Статус: {order.status_choice}. "
                        f"Общая сумма заказа {order.total_price} рублей. Доставка указана"
                        f"по адресу: город {order.delivery_contacts.city}, "
                        f"улица {order.delivery_contacts.street}, "
                        f"дом {order.delivery_contacts.house_number}"
                        f"квартира {order.delivery_contacts.apartment_number}"
                    }
                )
        except Order.DoesNotExist:
            return Response(
                {"status": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND
            )


def index(request):
    """
    Обработчик запроса для отображения главной страницы.

    Получает список всех магазинов (Shop) из базы данных и передает их в шаблон
    для отображения на главной странице.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные о запросе.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с данными о магазинах.
    """
    shops = Shop.objects.all()
    templates = "backend/index.html"
    context = {"shops": shops}
    return render(request, templates, context)


def register(request):
    """
    Обработчик запроса для регистрации нового пользователя.

    Если метод запроса POST, проверяет данные формы и создает нового пользователя.
    Отправляет письмо с подтверждением регистрации на email пользователя.
    Если метод запроса GET, отображает форму регистрации.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные и данные формы.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с формой регистрации
                        или перенаправление на другую страницу.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = str(uuid.uuid4())
            VerificationToken.objects.create(user=user, token=token)
            verification_url = request.build_absolute_uri(
                reverse_lazy("verify_email", args=[token])
            )

            try:
                email_text = f"Для подтверждения регистрации перейдите по ссылке: {verification_url}"
                subj_text = "Подтверждение регистрации"
                send_varif_mail(
                    host_email=smtp_user,
                    password=smtp_password,
                    user_email=user.email,
                    subj_tex=subj_text,
                    mail_text=email_text,
                )
                messages.success(
                    request,
                    f"Аккаунт {user.username} успешно создан! Проверьте почту для подтверждения.",
                )
            except Exception as e:
                print(f"Ошибка при отправке письма: {str(e)}")
                messages.error(request, f"Ошибка при отправке письма: {str(e)}")
                user.delete()
                return redirect("register")
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    templates = "backend/register.html"
    context = {"form": form}
    return render(request, templates, context)


def verify_email(request, token):
    """
    Обработчик запроса для подтверждения email пользователя.

    Проверяет валидность токена верификации. Если токен действителен,
    активирует аккаунт пользователя и удаляет токен. В противном случае
    выводит сообщение об ошибке.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные о запросе.
        - token (str): Уникальный токен для верификации email.

    Возвращает:
        - HttpResponse: Перенаправление на страницу входа с соответствующим сообщением.
    """
    try:
        verification_token = VerificationToken.objects.get(token=token)
        user = verification_token.user
        user.is_active = True
        user.save()
        verification_token.delete()
        messages.success(request, "Электронная почта успешно подтверждена!")
    except VerificationToken.DoesNotExist:
        messages.error(request, "Недействительный токен верификации.")

    return redirect("login")


def user_login(request):
    """
    Обработчик запроса для аутентификации пользователя.

    Если метод запроса POST, проверяет введенные данные (username и password)
    и аутентифицирует пользователя. При успешной аутентификации пользователь
    перенаправляется на главную страницу. В случае неудачи выводится сообщение
    об ошибке. Если метод запроса GET, отображается форма входа.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные и данные формы.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с формой входа
                        или перенаправление на другую страницу.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(
                request,
                "backend/login.html",
                {"error": "Неверное имя пользователя или пароль"},
            )
    else:
        return render(request, "backend/login.html")


def shop_categories(request, shop_id):
    """
    Обработчик запроса для отображения категорий товаров определенного магазина.

    Получает магазин по его ID и все категории товаров, связанные с этим магазином.
    Передает данные в шаблон для отображения на странице.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные о запросе.
        - shop_id (int): Идентификатор магазина, для которого нужно отобразить категории.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с данными о категориях товаров.
    """
    shop = get_object_or_404(Shop, id=shop_id)
    categories = ProductCategory.objects.filter(shop=shop)
    templates = "backend/shop_categories.html"
    context = {"shop": shop.name, "categories": categories}
    return render(request, templates, context)


def category_products(request, category_id):
    """
    Обработчик запроса для отображения товаров определенной категории.

    Получает категорию по её ID и все товары, связанные с этой категорией.
    Передает данные в шаблон для отображения на странице.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные о запросе.
        - category_id (int): Идентификатор категории, для которой нужно отобразить товары.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с данными о товарах.
    """
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=category)
    templates = "backend/category_products.html"
    context = {
        "shop": category.shop.name,
        "category": category.name,
        "products": products,
        "shop_id": category.shop.id,
    }
    return render(request, templates, context)


def product_detail(request, product_id):
    """
    Обработчик запроса для отображения детальной информации о товаре.

    Получает товар по его ID, а также связанные с ним данные (информацию о товаре и параметры).
    Передает данные в шаблон для отображения на странице.

    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные о запросе.
        - product_id (int): Идентификатор товара, для которого нужно отобразить детальную информацию.

    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с данными о товаре.
    """
    product = get_object_or_404(Product, id=product_id)
    info = ProductInfo.objects.filter(product=product)
    parameters = Parameters.objects.filter(product_info__product=product)
    templates = "backend/product_detail.html"
    context = {
        "product": product,
        "info": info,
        "parameters": parameters,
        "category_id": product.category.id,
    }
    return render(request, templates, context)


def profile(request):
    """
    Отображает профиль пользователя с историей его заказов.

    Функция извлекает все заказы текущего пользователя, сортируя их
    по дате создания в обратном порядке (от новых к старым).
    Полученные данные передаются в контекст шаблона для отображения
    на странице профиля.

    Параметры:
    - request (HttpRequest): Объект запроса Django, содержащий информацию
      о текущем пользователе и запросе.

    Возвращает:
    - HttpResponse: Отрендеренный HTML-шаблон с контекстом данных.
    """
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "orders": orders,
    }
    return render(request, "backend/profile.html", context)


def edit_profile(request):
    """
    Обработчик запроса для редактирования профиля пользователя.
    Если метод запроса POST, проверяет данные формы и обновляет информацию о пользователе.
    Если метод запроса GET, отображает форму редактирования профиля.
    Аргументы:
        - request (HttpRequest): Объект запроса, содержащий метаданные и данные формы.
    Возвращает:
        - HttpResponse: Ответ сервера, содержащий HTML-страницу с формой редактирования профиля
                        или перенаправление на другую страницу.
    """
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(
                "profile"
            )  # Перенаправление на страницу профиля после сохранения
    else:
        form = UserChangeForm(instance=request.user)

    templates = "backend/edit_profile.html"
    context = {"form": form}
    return render(request, templates, context)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("index")
    http_method_names = ["get", "post"]
