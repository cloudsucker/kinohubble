from typing import List, Dict, Union


PERSON_URL_TEMPLATE = "https://www.kinopoisk.ru/name/{}/"
FILM_URL_TEMPLATE = "https://www.kinopoisk.ru/film/{}/"
TVSERIES_URL_TEMPLATE = "https://www.kinopoisk.ru/series/{}/"


MEDIA_CONTENT_TYPES = {"tvseries": "tvSeries", "film": "film"}
REQUIRED_FIELDS: list = ["id", "typename"]


class MissingFieldError(Exception):
    """Exception raised when a required field is missing or empty."""

    pass


def get_full_url(url: str) -> str | None:
    return "https:" + url + "/orig/" if url else None


def filter_recursive(data: Union[List, Dict]) -> Union[List, Dict]:
    """
    Функция для удаления пустых значений и проверки обязательных
    полей во вложенных структурах dict и list.

    Args:
        data (Any): Данные для фильтрации.

    Returns:
        data (Any): Фильтрованные данные.
    """

    # LIST RECURSION FOR EACH ITEM
    if isinstance(data, list):
        filtered_list = []
        for item in data:
            if isinstance(item, dict):
                filtered_list.append(filter_recursive(item))
            else:
                filtered_list.append(item)
        return filtered_list

    # DICT RECURSION FOR EACH ITEM
    filtered_data = {}
    for key, value in data.items():

        # DICT RECURSION FOR EACH ITEM
        if isinstance(value, dict):
            filtered_value = filter_recursive(value)
            if filtered_value:
                filtered_data[key] = filtered_value

        # LIST RECURSION FOR EACH ITEM
        elif isinstance(value, list):
            filtered_list = []
            for item in value:
                if isinstance(item, dict):
                    filtered_item = filter_recursive(item)
                    if filtered_item:
                        filtered_list.append(filtered_item)
                else:
                    filtered_list.append(item)
            if filtered_list:
                filtered_data[key] = filtered_list

        # MAIN RECURSION LOGIC
        else:
            # VALIDATING REQUIRED FIELDS
            if key in REQUIRED_FIELDS:
                if not value:
                    raise MissingFieldError(f"Missing or empty required field: {key}")
                filtered_data[key] = value
            elif value:
                filtered_data[key] = value

    return filtered_data


def is_media_content_type_valid(content_type: str) -> bool:
    """
    Функция для валидации типа медиа-контента.
    Проверяет есть ли такой тип контента в MEDIA_CONTENT_TYPES.

    Args:
        content_type (str): Тип контента.

    Returns:
        bool: True, если тип контента валиден, иначе False.
    """

    if content_type in MEDIA_CONTENT_TYPES:
        return True
    return False
