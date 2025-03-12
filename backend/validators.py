import re
from django.core.exceptions import ValidationError


def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Пароль должен быть не короче 8 символов, содержать хотя бы одну маленькую букву и "
                              "прописную букву, хотя бы одну цифру.")

    if not re.search("[a-z]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну маленькую букву.")

    if not re.search("[A-Z]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну прописную букву.")

    if not re.search("[0-9]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну цифру.")