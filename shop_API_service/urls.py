"""
URL configuration for shop_API_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from backend.views import (ShopViewSet, ShopProductViewSet,
                           ProductCategoryViewSet, ProductsViewSet,
                           CreateProductCardViewSet, ImportProductsView,
                           UserViewSet, ParamsViewSet, OrderViewSet,
                           index, register, shop_categories, category_products,
                           product_detail, user_login, verify_email, profile, edit_profile,
                           CustomLogoutView)


router = DefaultRouter()
router.register('shops', ShopViewSet, basename='shop')
router.register('shop/product', ShopProductViewSet, basename='shop/product')
router.register('category', ProductCategoryViewSet, basename='category')
router.register('products', ProductsViewSet, basename='product')
router.register('create', CreateProductCardViewSet, basename='create')
router.register('account/registration', UserViewSet, basename='registration')
router.register('params', ParamsViewSet)
router.register('order', OrderViewSet, basename='order')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('import/', ImportProductsView.as_view(), name='import'),
    path('index/', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('shop_categories/<int:shop_id>', shop_categories, name='shop_categories'),
    path('category_products/<int:category_id>/', category_products, name='category_products'),
    path('product_detail/<int:product_id>/', product_detail, name='product_detail'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
    path('profile/', profile, name='profile'),
] + router.urls
