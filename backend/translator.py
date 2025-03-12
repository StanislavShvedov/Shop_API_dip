from translate import Translator


def translat_text_ru_en(text):
    ord_text = set(ord(s) for s in text if s.isalpha())
    if 1040 <= min(ord_text) and max(ord_text) <= 1103:
        translator = Translator(from_lang='ru', to_lang='en')
        translated_text = translator.translate(text)
        return translated_text
    else:
        return text


def translat_text_en_ru(text):
    ord_text = set(ord(s) for s in text if s.isalpha())
    if 65 <= min(ord_text) and max(ord_text) <= 122:
        translator = Translator(from_lang='en', to_lang='ru')
        translated_text = translator.translate(text)
        return translated_text
    else:
        return text


def translator_key(text):
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