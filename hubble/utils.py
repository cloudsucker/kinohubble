import re
import html
from typing import Any


def get_nested(
    data: Any, keys: str, required: bool = False, default: Any = None
) -> Any:
    """
    Функция для получения уникального значения вложенного словаря
    по ключу формата "key1.key2.key3".

    Parameters:
        data (dict): Словарь, в котором ищется значение.
        keys (str): Ключ вложенного словаря в формате "key1.key2.key3".
        required (bool): Флаг, указывающий на необходимость наличия значения вложенного словаря.
        default (any): Значение, которое будет возвращено в случае отсутствия значения вложенного словаря.

    Returns:
        any: Значение, найденное вложенным словаре.
    """

    keys = keys.split(".")

    for key in keys:

        # DICT PROCESSING
        if isinstance(data, dict):
            data = data.get(key, default)
            if data is default and required:
                raise KeyError(f"Required key '{key}' not found in the data.")

        # LIST PROCESSING
        elif isinstance(data, list):

            # CURRENT INDEX PROCESSING
            if key.isdigit():
                index = int(key)
                if index < len(data):
                    data = data[index]
                else:
                    data = default
                    if required:
                        raise KeyError(f"Required index {index} not found in the list.")

            # INDEX IN BRACKETS FORMAT PROCESSING
            elif ("[" in key) and ("]" in key):
                i1 = key.find("[") + 1
                i2 = key.find("]")
                key = int(key[i1:i2])

                if key < len(data):
                    data = data[key]
                else:
                    data = default
                    if required:
                        raise KeyError(f"Required index {key} not found in the list.")

            # LIST SKIPPING PROCESSING
            # (like a.b.c instead of a.b.0.c into {a: {b: [c]}})
            else:
                temp_list = []
                for item in data:
                    if isinstance(item, dict) and key in item:
                        temp_list.append(item[key])
                data = temp_list if temp_list else default
                data = data[0] if len(data) == 1 else data

        # OTHER TYPES UNSUPPORTED
        else:
            if required:
                raise KeyError(f"Required key '{key}' not found in the data.")
            return default

    return data


def remove_html_tags(text: str) -> str:
    """
    Функция для удаления HTML-тегов из текста.

    Parameters:
        text (str): Текст, в котором нужно удалить HTML-теги.

    Returns:
        str: Текст без HTML-тегов.
    """
    text = re.sub(r"<[^>]*>", "", text)
    text = html.unescape(text)
    return text
