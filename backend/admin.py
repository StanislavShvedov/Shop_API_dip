from django.contrib import admin
from django.utils.html import format_html
from .models import Shop, ShopProduct, OrderProduct, Order, ProductCategory, Product


# Register your models here.
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop', 'product', 'quantity']
    list_filter = ['shop', 'product']

admin.site.register(ShopProduct, ShopProductAdmin)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'shop']
    list_filter = ['user', 'shop']

admin.site.register(ProductCategory, ProductCategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'is_available', 'user']
    list_filter = ['name', 'category', 'is_available', 'user']
    search_fields = ['name', 'category__name']

admin.site.register(Product, ProductAdmin)


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('product', 'quantity')


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status_choice', 'updated_at', 'created_at', 'total_price']
    list_filter = ['user', 'status_choice']
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_link', 'shop_product_link', 'order_link', 'quantity']
    list_filter = ['product']

    @admin.display(description='Product')
    def product_link(self, obj):
        """
        Создает ссылку на страницу редактирования продукта.
        """
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/backend/product/{obj.product.pk}/change/',  # URL для редактирования продукта
            obj.product
        )

    @admin.display(description='Shop Product')
    def shop_product_link(self, obj):
        """
        Создает ссылку на страницу редактирования ShopProduct.
        """
        if obj.shop_product:  # Проверяем, существует ли связанный объект
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/backend/shopproduct/{obj.shop_product.pk}/change/',  # URL для редактирования ShopProduct
                obj.shop_product
            )
        return "No shop product"  # Если связанный объект отсутствует

    @admin.display(description='Order')
    def order_link(self, obj):
        """
        Создает ссылку на страницу редактирования заказа.
        """
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/backend/order/{obj.order.pk}/change/',  # URL для редактирования заказа
            obj.order
        )

admin.site.register(OrderProduct, OrderProductAdmin)