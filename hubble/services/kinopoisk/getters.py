from kinopapi import suggest_search_async
from kinopapi import person_preview_card_async
from kinopapi import film_trivias_async, tvseries_trivias_async
from kinopapi import film_base_info_async, tvseries_base_info_async
from kinopapi import film_similar_movies_async, tvseries_similar_movies_async
from kinopapi import film_media_posts_async, tvseries_media_posts_async

from hubble.utils import get_nested
from hubble.services.kinopoisk.parsers import parse_trivia_data
from hubble.services.kinopoisk.parsers import parse_film_data
from hubble.services.kinopoisk.parsers import parse_movie_data
from hubble.services.kinopoisk.parsers import parse_person_data
from hubble.services.kinopoisk.parsers import parse_tvseries_data
from hubble.services.kinopoisk.parsers import parse_media_post_data
from hubble.services.kinopoisk.service_utils import filter_recursive
from hubble.services.kinopoisk.service_utils import MEDIA_CONTENT_TYPES


async def get_search(query: str) -> None | dict | tuple[dict, dict]:
    """
    Функция для получения данных по запросу поиска Кинопоиск API.
    При значении debug=True возвращает кортеж из двух словарей,
    где первый - оригинальный json, второй - содержащий только необходимые данные после парсинга.

    Parameters:
        query (str): Запрос поиска.
    """

    response = await suggest_search_async(query)
    if not response or not response.ok:
        return

    response_data = await response.json()

    # ROOT:
    json_root = get_nested(response_data, "data.suggest.top")

    parsed_data = {}
    if json_root:
        # 0. TOP_RESULT PROCESSING:
        match = get_nested(json_root, "topResult.global")
        typename = get_nested(match, "__typename")

        # 1. SEARCH MATCH PROCESSING:
        match_processed_data = None
        if typename == "Person":
            match_processed_data = parse_person_data(match)
        elif typename == "TvSeries":
            match_processed_data = parse_tvseries_data(match)
        elif typename == "Film":
            match_processed_data = parse_film_data(match)

        # 2. OTHER MOVIES PROCESSING:
        movies = get_nested(json_root, "movies")
        processed_movies = []
        if movies:
            for movie in movies:
                movie_data = get_nested(movie, "movie")
                processed_movie = parse_movie_data(movie_data)
                processed_movies.append(processed_movie)

        # 3. OTHER PERSONS PROCESSING:
        persons = get_nested(json_root, "persons")
        processed_persons = []
        if persons:
            for person in persons:
                person_data = get_nested(person, "person")
                processed_persons.append(parse_person_data(person_data))

        # 4. OTHER CINEMAS PROCESSING (NO CINEMAS IN RESPONSES YET)
        # cinemas = get_nested(json_root, "cinemas")
        # cinemas = None
        # if cinemas:
        #     raise Exception(f"CINEMAS_FOUNDED: \n\n{cinemas}")

        # 5. OTHER MOVIELISTS PROCESSING (NO MOVIELISTS IN RESPONSES YET)
        # movie_lists = get_nested(json_root, "movieLists")
        # movie_lists = None
        # if movie_lists:
        #     raise Exception(f"MOVIELISTS_FOUNDED: \n\n{movie_lists}")

        parsed_data = {
            "match": match_processed_data,
            "movies": processed_movies,
            "persons": processed_persons,
            # "cinemas": cinemas,
            # "movie_lists": movie_lists,
            "typename": "search_result",
        }

        parsed_data = filter_recursive(parsed_data)
        if parsed_data.keys() == {"typename"}:
            parsed_data = {}
    return parsed_data


async def get_info(content_type: str, id: int) -> None | dict | tuple[dict, dict]:
    """
    Функция для получения данных о фильмах и сериалах используя два разных запроса
    к API Кинопоиск в зависимости от типа контента.

    Parameters:
        content_type (str): Тип контента: 'film' или 'tvseries'.
        id (int): ID контента.

    Returns:
        dict | tuple[dict, dict]: Обработанные данные или кортеж из двух словарей,
        где первый - оригинальный json, второй - содержащий только необходимые данные после парсинга.
    """

    ct_key = get_nested(MEDIA_CONTENT_TYPES, content_type)

    if content_type == "film":
        response = await film_base_info_async(id)
    elif content_type == "tvseries":
        response = await tvseries_base_info_async(id)

    if not response or not response.ok:
        return

    response_data = await response.json()

    root = get_nested(response_data, f"data.{ct_key}")

    # TODO: BETTER TO CHECK THERE IS NO ERROR RESPONSED
    # errors = get_nested(json_data, "errors")

    parsed_data = {}
    if root:
        parsed_data = parse_movie_data(root)
        parsed_data = filter_recursive(parsed_data)

    return parsed_data


async def get_similars(
    content_type: str, id: int
) -> None | list[dict] | tuple[dict, list[dict]]:
    """
    Функция для получения данных о похожих фильмах и сериалах используя два разных запроса
    к API Кинопоиск в зависимости от типа контента.

    Parameters:
        content_type (str): Тип контента: 'film' или 'tvseries'.
        id (int): ID контента.

    Returns:
        list[dict] | tuple[dict, list[dict]]: Обработанные данные или кортеж из двух словарей,
        где первый - оригинальный json, второй - содержащий только необходимые данные после парсинга.
    """

    ct_key = get_nested(MEDIA_CONTENT_TYPES, content_type, required=True)

    if content_type == "film":
        response = await film_similar_movies_async(filmId=id)
    elif content_type == "tvseries":
        response = await tvseries_similar_movies_async(tvseries_id=id)

    if not response or not response.ok:
        return

    response_data = await response.json()
    root = get_nested(response_data, f"data.{ct_key}.userRecommendations")

    parsed_data = []
    if root:
        movies_items = get_nested(root, "items")

        for movie_item in movies_items:
            movie_data = get_nested(movie_item, "movie")

            # SEEMS LIKE NO TVSERIES RECOMMENDATIONS HERE. TESTING THIS YET...
            processed_movie_data = parse_movie_data(movie_data)

            parsed_data.append(processed_movie_data)

        parsed_data = filter_recursive(parsed_data)

    return parsed_data


async def get_person(id: int) -> None | dict | tuple[dict, dict]:
    response = await person_preview_card_async(id)

    if not response or not response.ok:
        return

    response_data = await response.json()
    person_root = get_nested(response_data, "data.person")

    parsed_data = {}
    if person_root:
        parsed_data = parse_person_data(person_root)
        parsed_data = filter_recursive(parsed_data)

    return parsed_data


async def get_trivias(
    content_type: str, id: int
) -> None | list[dict] | tuple[dict, list[dict]]:
    ct_key = get_nested(MEDIA_CONTENT_TYPES, content_type, required=True)

    if content_type == "film":
        response = await film_trivias_async(film_id=id)
    elif content_type == "tvseries":
        response = await tvseries_trivias_async(tvseries_id=id)

    if not response or not response.ok:
        return

    response_data = await response.json()
    parsed_data = []
    if response_data:
        _trivias_items = get_nested(response_data, f"data.{ct_key}.trivias.items")

        if _trivias_items:
            for _trivia_item in _trivias_items:
                parsed_trivia = parse_trivia_data(_trivia_item)
                parsed_data.append(parsed_trivia)

        parsed_data = filter_recursive(parsed_data)

    return parsed_data


async def get_media_posts(
    content_type: str, id: int
) -> None | list[dict] | tuple[dict, list[dict]]:
    ct_key = get_nested(MEDIA_CONTENT_TYPES, content_type, required=True)

    if content_type == "film":
        response = await film_media_posts_async(film_id=id)
    elif content_type == "tvseries":
        response = await tvseries_media_posts_async(tvseries_id=id)

    if not response or not response.ok:
        return

    response_data = await response.json()

    parsed_data = []
    if response_data:
        _media_posts_items = get_nested(
            response_data, f"data.{ct_key}.mediaPosts.items"
        )
        if _media_posts_items:
            for _media_post_item in _media_posts_items:
                parsed_media_post_item = parse_media_post_data(_media_post_item)
                parsed_data.append(parsed_media_post_item)

    parsed_data = filter_recursive(parsed_data)

    return parsed_data
