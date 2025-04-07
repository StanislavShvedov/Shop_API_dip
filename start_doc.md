Запуск сервера
1. Установка зависимостей
 - pip install -r requirements.txt

2. Настройка базы данных
 - python manage.py makemigrations # создаем миграцию
 - python manage.py migrate # применяем миграцию
 - python manage.py createsuperuser # создаем суперпользователя

3. Запуск сервера
 - python manage.py runserver # запускаем сервер

4. Создайте файл .env, внесите в него следующие данные:
 - POSTGRES_USER = "Имя Вашего пользователя базы данных"
 - POSTGRES_PASSWORD = "Ваш пароль пользователя базы данных"
 - POSTGRES_DB = "Название Вашей базы данных"
 - POSTGRES_HOST = "127.0.0.1"
 - POSTGRES_PORT = "5432"
 - smtp_user = "Ваша почта@yandex.ru"
 - smtp_password = "Пароль приложения"
 - GOOGLE_CLIENT_ID="Ваш id приложения"
 - GOOGLE_CLIENT_SECRET="Ваш ключ приложения"

7. Доступные endpoints API

После запуска сервера будут доступны следующие API endpoints:

/api/shops/ - CRUD операции для магазинов
/api/shop-products/ - CRUD операции для товаров магазина
/api/product-categories/ - CRUD операции для категорий товаров
/api/products/ - CRUD операции для товаров
/api/create-product-card/ - Создание карточки товара
/api/import-products/ - Импорт товаров из YAML (файл или url)
/api/users/ - CRUD операции для пользователей
/api/params/ - CRUD операции для параметров товаров
/api/orders/ - CRUD операции для заказов

8. Веб-интерфейс

Для веб-интерфейса доступны следующие страницы:

Главная страница (index/)
Регистрация (/register/)
Вход (/login/)
Профиль пользователя (/profile/)
Редактирование профиля (/edit-profile/)
Подтверждение email (/verify-email/<token>/)
Категории магазина (/shop/<shop_id>/categories/)
Товары категории (/category/<category_id>/products/)
Детали товара (/product/<product_id>/)

9. Проверка работоспособности

После запуска проверьте работу всех основных функций:

Регистрация нового пользователя и подтверждение email
Вход в систему
Создание магазина и добавление товаров
Создание заказа
Импорт товаров из YAML

10. Административная панель

Для управления контентом через административную панель перейдите по адресу /admin/ и 
войдите с учетными данными суперпользователя.

11. Примеры запросов rest-client (VSCode):

GET http://127.0.0.1:8000/shops/

### Публикуем магазин
POST http://127.0.0.1:8000/shops/
Content-Type: application/json
Authorization: Token bfdc7f16bdf14b837bed56beb9a65e6077e3520b

{
    "name": "shop1"
}

### Удаляем магазин
DELETE http://127.0.0.1:8000/shops/5/
Authorization: Token 9d4744b58637564c200f7a2ed289c345e50e1880

### Получаем инфо магазина
GET http://127.0.0.1:8000/shops/5/
Authorization: Token 9d4744b58637564c200f7a2ed289c345e50e1880

### Импорт каталога товаров
POST http://127.0.0.1:8000/import/
Content-Type: application/json
Authorization: Token 650aa235ca4355203d9910775db81893414a5b03

{
    "url": "https://raw.githubusercontent.com/netology-code/python-final-diplom/master/data/shop1.yaml"
}

### Получение информации о продуктaх
GET http://127.0.0.1:8000/products/

### Получение информации о продукте
GET http://127.0.0.1:8000/products/4672670/

### Создание заказа
POST http://127.0.0.1:8000/order/
Authorization: Token e7ba18daeb804f9e16e122bc0b748ca18ca50508 ### замените на свой токен

### Получение списка заказов
GET http://127.0.0.1:8000/order/
Authorization: Token e7ba18daeb804f9e16e122bc0b748ca18ca50508 ### замените на свой токен

### Создание заказа
POST http://127.0.0.1:8000/order/
Content-Type: application/json
Authorization: Token e7ba18daeb804f9e16e122bc0b748ca18ca50508 ### замените на свой токен

{
}

### Добавление продукта в заказ
POST http://127.0.0.1:8000/order/add_product/
Content-Type: application/json
Authorization: Token 650aa235ca4355203d9910775db81893414a5b03 ### замените на свой токен

{
    "product_id": 4216226,
    "quantity": 1
}

### Удаление продукта
POST http://127.0.0.1:8000/order/delete_product/
Content-Type: application/json
Authorization: Token 650aa235ca4355203d9910775db81893414a5b03 ### замените на свой токен

{
    "product_id": 4216226,
    "quantity": 1
}

### Завершение заказа(самовывоз)
POST http://127.0.0.1:8000/order/place_an_order/
Content-Type: application/json
Authorization: Token 650aa235ca4355203d9910775db81893414a5b03 ### замените на свой токен

{

}

### Завершение заказа(доставка)
POST http://127.0.0.1:8000/order/place_an_order/
Content-Type: application/json
Authorization: Token 650aa235ca4355203d9910775db81893414a5b03 ### замените на свой токен

{
    "delivery_choice": true,
    "city": "Moscow",
    "street": "Ylica",
    "house_number": "djff",
    "apartment_number": "dafsg",
    "phone_number": "23241"
}

### Выключение/включение продукта
POST http://127.0.0.1:8000/products/disable_enabled_product/
Content-Type: application/json
Authorization: Token e7ba18daeb804f9e16e122bc0b748ca18ca50508 ### замените на свой токен

{
    "product_id": "4216226"
}

12. Тестирование

    ### Запуск тестов
    - coverage run -m pytest
    
    ### Отчет о тестах
    - coverage report
    - coverage html
    - open htmlcov/index.htm # открываем в браузере

13. Документация

    - http://127.0.0.1:8000/
    - http://127.0.0.1:8000/api/docs/swagger/
    - http://127.0.0.1:8000/api/docs/redoc/
    - http://127.0.0.1:8000/api/schema/
