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
                           UserViewSet, ParamsViewSet)


router = DefaultRouter()
router.register('shops', ShopViewSet, basename='shop')
router.register('shop/product', ShopProductViewSet, basename='shop/product')
router.register('category', ProductCategoryViewSet, basename='category')
router.register('products', ProductsViewSet, basename='product')
router.register('create', CreateProductCardViewSet, basename='create')
router.register('account/registration', UserViewSet, basename='registration')
router.register('params', ParamsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('import/', ImportProductsView.as_view(), name='import'),
] + router.urls
