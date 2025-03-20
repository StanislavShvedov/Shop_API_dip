from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
        Разрешение для владельца объекта или только для чтения.

        Позволяет выполнять операции чтения (GET) всем пользователям.
        Для операций изменения (POST, PUT, DELETE) доступ разрешен только владельцу объекта.

        Методы:
            - has_object_permission(request, view, obj) -> bool:
                Проверяет, имеет ли пользователь право на выполнение действия с объектом.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        """
            Аргументы:
                - request: Объект запроса.
                - view: Объект представления.
                - obj: Объект, к которому запрашивается доступ.

            Возвращает:
                - bool: True, если доступ разрешен, иначе False.
        """
        if request.method == 'GET':
            return True
        return request.user == obj.user


class IsOwner(BasePermission):
    """
        Разрешение только для владельца.

        Проверяет, авторизован ли пользователь и является ли он владельцем объекта.

        Методы:
            - has_permission(request, view) -> bool:
                Проверяет, имеет ли пользователь право на выполнение действия.
    """
    def has_permission(self, request, view) -> bool:
        """
           Аргументы:
                - request: Объект запроса.
                - view: Объект представления.

            Возвращает:
                - bool: True, если пользователь авторизован, иначе False.
        """
        return request.user
