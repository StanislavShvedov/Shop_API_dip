import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from backend.models import Shop, ProductCategory, Product

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass1234")

@pytest.mark.django_db
def test_index_view(client):
    response = client.get(reverse('index'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_view(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'password': 'password123',
        'email': 'test@example.com'
    })
    assert response.status_code in [200, 302]

@pytest.mark.django_db
def test_login_view(client, user):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'pass1234'
    })
    assert response.status_code in [200, 302]

@pytest.mark.django_db
def test_logout_view(client, user):
    client.force_login(user)
    response = client.get(reverse('logout'))
    assert response.status_code in [200, 302]

@pytest.mark.django_db
def test_profile_view_authenticated(client, user):
    client.force_login(user)
    response = client.get(reverse('profile'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_verify_email_invalid_token(client):
    response = client.get(reverse('verify_email', args=["invalidtoken"]))
    assert response.status_code in [400, 404, 200, 302]

@pytest.mark.django_db
def test_shop_categories_view(client, db, user):
    shop = Shop.objects.create(name="Test Shop", user=user)
    response = client.get(reverse('shop_categories', args=[shop.id]))
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_category_products_view(client, db, user):
    shop = Shop.objects.create(name="Test Shop", user=user)
    category = ProductCategory.objects.create(name="Test Category", user=user, shop=shop)
    response = client.get(reverse('category_products', args=[category.id]))
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_product_detail_view(client, db, user):
    shop = Shop.objects.create(name="Test Shop", user=user)
    category = ProductCategory.objects.create(name="Test Category", user=user, shop=shop)
    product = Product.objects.create(name="Product", category=category, user=user)
    response = client.get(reverse('product_detail', args=[product.id]))
    assert response.status_code in [200, 404]