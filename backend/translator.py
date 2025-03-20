from translate import Translator


def translat_text_ru_en(text: str) -> str:
    """
        Переводит текст с русского языка на английский.

        Функция проверяет, является ли текст написанным кириллицей (русский язык),
        и переводит его на английский. Если текст уже написан латиницей, возвращает его без изменений.

        Аргументы:
            - text (str): Исходный текст для перевода.

        Возвращает:
            - str: Переведенный текст или исходный текст, если перевод не требуется.
    """
    ord_text = set(ord(s) for s in text if s.isalpha())
    if 1040 <= min(ord_text) and max(ord_text) <= 1103:
        translator = Translator(from_lang='ru', to_lang='en')
        translated_text = translator.translate(text)
        return translated_text
    else:
        return text


def translat_text_en_ru(text: str) -> str:
    """
        Переводит текст с английского языка на русский.

        Функция проверяет, является ли текст написанным латиницей (английский язык),
        и переводит его на русский. Если текст уже написан кириллицей, возвращает его без изменений.

        Аргументы:
            - text (str): Исходный текст для перевода.

        Возвращает:
            - str: Переведенный текст или исходный текст, если перевод не требуется.
    """
    ord_text = set(ord(s) for s in text if s.isalpha())
    if 65 <= min(ord_text) and max(ord_text) <= 122:
        translator = Translator(from_lang='en', to_lang='ru')
        translated_text = translator.translate(text)
        return translated_text
    else:
        return text


def translator_key(text: str) -> str:
    """
        Переводит ключевые слова из русского языка на английский.

        Функция проверяет, является ли текст написанным кириллицей (русский язык),
        и переводит ключевые слова из словаря fields_value на английский язык.
        Если текст уже написан латиницей, возвращает его без изменений.

        Аргументы:
            - text (str): Исходный текст для перевода.

        Возвращает:
            - str: Переведенный текст или исходный текст, если перевод не требуется.
    """
    fields_value = {'Диагональ (дюйм)': 'Screen Size (inches)',
                    'Разрешение (пикс)': 'Resolution (pixels)',
                    'Встроенная память (Гб)': 'Internal Memory (GB)',
                    'Цвет': 'Color',
                    'Умный': 'Smart TV',
                    'Ёмкость': 'Capacity (GB)'}
    ord_text = set(ord(s) for s in text if s.isalpha())
    if 1040 <= min(ord_text) and max(ord_text) <= 1103:
        try:
            for key, value in fields_value.items():
                if key in text:
                    return value
        except Exception as e:
            return f"Error: {e}"
    else:
        return text
