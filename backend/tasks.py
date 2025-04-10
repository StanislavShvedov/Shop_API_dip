import os
from celery import shared_task
import yaml
import requests
from django.core.files import File
from django.conf import settings

from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO


from .models import Shop, ProductCategory, Product, ShopProduct, ProductInfo, Parameters, UserProfile
from .translator import translat_text_en_ru, translat_text_ru_en, translator_key


@shared_task()
def import_products_task(data, user):
    """
    Задача Celery для асинхронного импорта товаров из YAML-данных.
    """
    try:
        parameters_instance = None

        for key, values in data.items():
            if key == "shop":
                if Shop.objects.filter(name=values).exists():
                    shop_instance = Shop.objects.get(name=values)
                else:
                    try:
                        shop_instance = Shop.objects.create(user=user, name=values)
                    except Exception as e:
                        return Response({"status": f"Error: {e}"})

            if key == "categories":
                for category in values:
                    if ProductCategory.objects.filter(name=category["name"]).exists():
                        continue
                    else:
                        try:
                            ProductCategory.objects.create(
                                user=user,
                                id=category["id"],
                                name=category["name"],
                                shop=shop_instance,
                            )
                        except Exception as e:
                            return Response({"status": f"Error: {e}"})

            if key == "goods":
                for product in values:
                    if Product.objects.filter(id=product["id"]).exists():
                        product_instance = Product.objects.get(id=product["id"])
                        return Response(
                            {
                                "status": f'Товар {product_instance.name} с ID: {product["id"]} уже существует'
                            }
                        )
                    try:

                        category_instance = ProductCategory.objects.get(
                            id=product["category"]
                        )
                        product_instance = Product.objects.create(
                            user=user,
                            id=product["id"],
                            name=translat_text_en_ru(product["name"]),
                            category=category_instance,
                        )

                        ShopProduct.objects.create(
                            user=user,
                            shop=shop_instance,
                            product=product_instance,
                            quantity=product["quantity"],
                        )

                        info_instance = ProductInfo.objects.create(
                            user=user,
                            model=product["model"],
                            price=product["price"],
                            price_rrc=product["price_rrc"],
                            product=product_instance,
                        )

                        if product["parameters"]:
                            screen_size = None
                            resolution = None
                            internal_memory = None
                            color = None
                            smart_tv = None
                            capacity = None

                            for key_name, value in product["parameters"].items():
                                if (
                                    product_instance.category.name == "Смартфоны"
                                    or product_instance.category.name == "Аксессуары"
                                ):
                                    if (
                                        translator_key(key_name)
                                        == "Screen Size (inches)"
                                    ):
                                        screen_size = value
                                    if (
                                        translator_key(key_name)
                                        == "Resolution (pixels)"
                                    ):
                                        resolution = value
                                    if (
                                        translator_key(key_name)
                                        == "Internal Memory (GB)"
                                    ):
                                        internal_memory = value
                                    if translator_key(key_name) == "Color":
                                        color = value

                                elif (
                                    product_instance.category.name == "Flash-накопители"
                                ):
                                    if translator_key(key_name) == "Color":
                                        color = value
                                    if translator_key(key_name) == "Capacity (GB)":
                                        capacity = value

                                elif product_instance.category.name == "Телевизоры":
                                    if (
                                        translator_key(key_name)
                                        == "Screen Size (inches)"
                                    ):
                                        screen_size = value
                                    if (
                                        translator_key(key_name)
                                        == "Resolution (pixels)"
                                    ):
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
                                product_info=info_instance,
                            )

                    except Exception as e:
                        if yaml_file:
                            return Response(
                                {
                                    "status": f"Произошла ошибка при импорте продуктов из каталога {yaml_file}: {e}"
                                }
                            )
                        elif yaml_url:
                            return Response(
                                {
                                    "status": f"Произошла ошибка при импорте продуктов из каталога {yaml_url}: {e}"
                                }
                            )

    except Exception as e:
        return e

def generate_thumbnail(image_path, size=(300, 300)):
    img = Image.open(image_path)
    img.convert('RGB')  # Ensure compatibility
    img.thumbnail(size)
    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG')
    return thumb_io


@shared_task
def generate_product_thumbnail(product_id):
    product = Product.objects.get(id=product_id)
    if not product.image:
        return

    thumb_io = generate_thumbnail(product.image.path)
    thumb_name = os.path.basename(product.image.name)
    product.thumbnail.save(f"thumb_{thumb_name}", File(thumb_io), save=True)


@shared_task
def generate_avatar_thumbnail(profile_id):
    profile = UserProfile.objects.get(id=profile_id)
    if not profile.avatar:
        return

    thumb_io = generate_thumbnail(profile.avatar.path, size=(150, 150))
    thumb_name = os.path.basename(profile.avatar.name)
    profile.avatar_thumbnail.save(f"thumb_{thumb_name}", File(thumb_io), save=True)


