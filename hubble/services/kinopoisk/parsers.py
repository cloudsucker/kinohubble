from datetime import datetime
from hubble.utils import get_nested, remove_html_tags
from hubble.services.kinopoisk.service_utils import get_full_url
from hubble.services.kinopoisk.service_utils import FILM_URL_TEMPLATE
from hubble.services.kinopoisk.service_utils import PERSON_URL_TEMPLATE
from hubble.services.kinopoisk.service_utils import TVSERIES_URL_TEMPLATE


def parse_person_data(person_data: dict) -> dict:
    """
    Функция для парсинга блока данных о персоне кино.

    Parameters:
        person_data (dict): Словарь с данными о персоне, с ключом '__typename'
        со значением 'Person'.

    Returns:
        dict: Словарь с отфильтрованными данными о персоне, содержащий ключ 'typename' со значением 'Person'.
    """

    typename = get_nested(person_data, "__typename")
    typename = str(typename).lower()

    if typename != "person":
        raise ValueError(
            f"Error: parse_person_data function got '__typename': '{typename}', expected 'person'."
        )

    # BASE DATA
    id = get_nested(person_data, "id", required=True)
    name = get_nested(person_data, "name")
    original_name = get_nested(person_data, "originalName")
    birth_date = get_nested(person_data, "birthDate")
    _avatars_pre_url = get_nested(person_data, "poster.avatarsUrl")
    avatars_url = get_full_url(_avatars_pre_url)

    # BEST PERSON FILMS
    best_films = []
    _best_films_items = get_nested(person_data, "bestFilms.items")
    if _best_films_items:
        for _best_films_item in _best_films_items:
            _movie_data = get_nested(_best_films_item, "movie")
            _parsed_movie_data = parse_movie_data(_movie_data)
            best_films.append(_parsed_movie_data)

    # BEST PERSON TVSERIES
    best_tvseries = []
    _best_tvseries_items = get_nested(person_data, "bestSeries.items")
    if _best_tvseries_items:
        for _best_tvseries_item in _best_tvseries_items:
            _movie_data = get_nested(_best_tvseries_item, "movie")
            _parsed_movie_data = parse_movie_data(_movie_data)
            best_tvseries.append(_parsed_movie_data)

    # PERSON ROLES (DIRECTOR / ACTOR / PRODUCER)
    roles = []
    _roles_items = get_nested(person_data, "roles.items")
    if _roles_items:
        for _role_item in _roles_items:
            role = get_nested(_role_item, "role.title.russian")
            roles.append(role)

    person_url = PERSON_URL_TEMPLATE.format(id)

    parsed_data = {
        "id": id,
        "name": name,
        "original_name": original_name,
        "birth_date": birth_date,
        "roles": roles,
        "avatars_url": avatars_url,
        "best_films": best_films,
        "best_tvseries": best_tvseries,
        "person_url": person_url,
        "typename": typename,
    }

    return parsed_data


def parse_country(country_data: dict) -> dict:
    """
    Функция для парсинга блока данных о стране.

    Parameters:
        country_data (dict): Словарь с данными о стране, с ключом '__typename'
        со значением 'Country'.

    Returns:
        dict: Словарь с отфильтрованными данными о стране, содержащий ключ 'typename' со значением 'Country'.
    """

    typename = get_nested(country_data, "__typename")
    typename = str(typename).lower()

    if typename != "country":
        raise ValueError(
            f"Error: parse_country function got '__typename': '{typename}', expected 'country'."
        )

    id = get_nested(country_data, "id", required=True)
    name = get_nested(country_data, "name")

    parsed_data = {
        "id": id,
        "name": name,
        "typename": typename,
    }

    return parsed_data


def parse_genre(genre_data: dict) -> dict:
    """
    Функция для парсинга блока данных о жанре.

    Parameters:
        genre_data (dict): Словарь с данными о жанре, с ключом '__typename'
        со значением 'Genre'.

    Returns:
        dict: Словарь с отфильтрованными данными о жанре, содержащий ключ 'typename' со значением 'Genre'.
    """

    typename = get_nested(genre_data, "__typename")
    typename = str(typename).lower()

    if typename != "genre":
        raise ValueError(
            f"Error: parse_genre got '__typename': '{typename}', expected 'genre'."
        )

    parsed_data = {
        "id": get_nested(genre_data, "id", required=True),
        "name": get_nested(genre_data, "name"),
        "slug": get_nested(genre_data, "slug"),
        "typename": typename,
    }

    return parsed_data


def parse_sequels_prequels_items(
    sequels_prequels_items: dict,
) -> tuple[dict, dict]:
    """
    Функция для парсинга блока данных о сиквелах и приквелах фильмов и сериалов.

    Parameters:
        sequels_prequels_items (dict): Словарь с данными о сиквелах и приквелах.

    Returns:
        tuple[dict, dict]: Кортеж из списков с данными о сиквелах и приквелах.
    """

    sequels = []
    prequels = []

    if not sequels_prequels_items:
        return sequels, prequels

    for _item_field in sequels_prequels_items:
        _relation_type = get_nested(_item_field, "relationType")
        _movie_data = get_nested(_item_field, "movie")
        typename = get_nested(_movie_data, "__typename")

        # PROCESSING DATA BY TYPENAME
        if typename == "Film":
            processed_data = parse_film_data(_movie_data)
        elif typename == "TvSeries":
            processed_data = parse_tvseries_data(_movie_data)

        # PACKING IT INTO PREQUELS OR SEQUELS
        if _relation_type == "BEFORE":
            prequels.append(processed_data)
        elif _relation_type == "AFTER":
            sequels.append(processed_data)

    parsed_data = sequels, prequels
    return parsed_data


def parse_tvseries_data(tvseries_data: dict):
    """
    Функция для парсинга блока данных о сериале.

    Parameters:
        tvseries_data (dict): Словарь с данными о сериале, с ключом '__typename'
        со значением 'TvSeries'.

    Returns:
        dict: Словарь с отфильтрованными данными о сериале, содержащий ключ typename со значением 'TvSeries'.
    """

    typename = get_nested(tvseries_data, "__typename")
    typename = str(typename).lower()

    if typename != "tvseries":
        raise ValueError(
            f"Error: parse_tvseries_data got '__typename': {typename}, expected 'tvseries'."
        )

    # BASE DATA
    id = get_nested(tvseries_data, "id", required=True)
    title_russian = get_nested(tvseries_data, "title.russian")
    title_original = get_nested(tvseries_data, "title.original")
    production_year = get_nested(tvseries_data, "productionYear")
    short_description = get_nested(tvseries_data, "shortDescription")
    synopsis = get_nested(tvseries_data, "synopsis")
    release_start = get_nested(tvseries_data, "releaseYears.start")
    release_end = get_nested(tvseries_data, "releaseYears.end")

    # GENRES
    genres = []
    _genres_field = get_nested(tvseries_data, "genres")
    if _genres_field:
        for _genre_field in _genres_field:
            parsed_genre = parse_genre(_genre_field)
            genres.append(parsed_genre)

    # COUNTRIES
    countries = []
    _countries_field = get_nested(tvseries_data, "countries")
    if _countries_field:
        for _country_field in _countries_field:
            parsed_country = parse_country(_country_field)
            countries.append(parsed_country)

    # SEASONS COUNT AND URLS
    seasons_count = get_nested(tvseries_data, "seasons.total")
    _cover_pre_url = get_nested(tvseries_data, "cover.image.avatarsUrl")
    cover_url = get_full_url(_cover_pre_url)
    trailer_stream_url = get_nested(tvseries_data, "mainTrailer.streamUrl")
    trailer_youtube = get_nested(tvseries_data, "mainTrailer.sourceVideoUrl")

    # ACTORS
    actors = []
    _actors_field = get_nested(tvseries_data, "actors")
    if _actors_field:
        actors_items = get_nested(_actors_field, "items")
        for _actor_item in actors_items:
            person_data = get_nested(_actor_item, "person")
            actors.append(parse_person_data(person_data))

    # VOICE OVER ACTORS
    voice_over_actors = []
    _voice_actors_field = get_nested(tvseries_data, "voiceOverActors")
    if _voice_actors_field:
        _voice_over_actors_items = get_nested(_voice_actors_field, "items")
        for _voice_over_actor_item in _voice_over_actors_items:
            person_data = get_nested(_voice_over_actor_item, "person")
            voice_over_actors.append(parse_person_data(person_data))

    # TAGLINE
    tagline = get_nested(tvseries_data, "tagline")

    # DIRECTORS
    directors = []
    _directors_field = get_nested(tvseries_data, "directors")
    if _directors_field:
        _directors_items = get_nested(_directors_field, "items")
        for _director_item in _directors_items:
            person_data = get_nested(_director_item, "person")
            directors.append(parse_person_data(person_data))

    # TODO: ADD:
    #   - WRITERS
    #   - PRODUCERS
    #   - OPERATORS
    #   - COMPOSERS
    #   - BOX_OFFICE

    # POSTER
    _poster_pre_url = get_nested(tvseries_data, "poster.avatarsUrl")
    poster_url = get_full_url(_poster_pre_url)

    # RATINGS
    rating_imdb = get_nested(tvseries_data, "rating.imdb.value")
    rating_kinopoisk = get_nested(tvseries_data, "rating.kinopoisk.value")
    rating_kinopoisk_top10_pos = get_nested(tvseries_data, "ratingLists.top10.position")
    rating_kinopoisk_top250_pos = get_nested(
        tvseries_data, "ratingLists.top250.position"
    )
    rating_russian_critics = get_nested(tvseries_data, "rating.russianCritics.value")
    rating_worldwide_critics = get_nested(
        tvseries_data, "rating.worldwideCritics.value"
    )

    # DURATIONS
    duration_total = get_nested(tvseries_data, "totalDuration")
    duration_series = get_nested(tvseries_data, "seriesDuration")

    # SEQUELS & PREQUELS
    sequels = []
    prequels = []
    _sequels_prequels_items = get_nested(tvseries_data, "sequelsPrequels.items")
    if _sequels_prequels_items:
        sequels, prequels = parse_sequels_prequels_items(_sequels_prequels_items)

    # URL
    url = TVSERIES_URL_TEMPLATE.format(id)

    parsed_data = {
        "id": id,
        "title_russian": title_russian,
        "title_original": title_original,
        "production_year": production_year,
        "short_description": short_description,
        "synopsis": synopsis,
        "release_start": release_start,
        "release_end": release_end,
        "genres": genres,
        "countries": countries,
        "seasons_count": seasons_count,
        "cover_url": cover_url,
        "trailer_stream_url": trailer_stream_url,
        "trailer_youtube": trailer_youtube,
        "actors": actors,
        "voice_over_actors": voice_over_actors,
        "tagline": tagline,
        "directors": directors,
        "poster_url": poster_url,
        "rating_imdb": rating_imdb,
        "rating_kinopoisk": rating_kinopoisk,
        "rating_kinopoisk_top10_pos": rating_kinopoisk_top10_pos,
        "rating_kinopoisk_top250_pos": rating_kinopoisk_top250_pos,
        "rating_russian_critics": rating_russian_critics,
        "rating_worldwide_critics": rating_worldwide_critics,
        "duration_total": duration_total,
        "duration_series": duration_series,
        "sequels": sequels,
        "prequels": prequels,
        "url": url,
        "typename": typename,
    }

    return parsed_data


def parse_film_data(film_data: dict) -> dict:
    """
    Функция для парсинга блока данных о фильме.

    Parameters:
        film_data (dict): Словарь с данными о фильме, с ключом '__typename'
        со значением 'Film'.

    Returns:
        dict: Словарь с отфильтрованными данными о фильме, содержащий ключ 'typename' со значением 'Film'.
    """
    typename = get_nested(film_data, "__typename")
    typename = str(typename).lower()

    if typename != "film":
        raise ValueError(
            f"Error: parse_film_data function got '__typename': {typename}, expected 'Film'."
        )

    # BASE DATA
    id = get_nested(film_data, "id", required=True)
    title_russian = get_nested(film_data, "title.russian")
    title_original = get_nested(film_data, "title.original")
    production_year = get_nested(film_data, "productionYear")
    short_description = get_nested(film_data, "shortDescription")
    synopsis = get_nested(film_data, "synopsis")

    # GENRES
    genres = []
    _genres_field = get_nested(film_data, "genres")
    if _genres_field:
        for _genre_field in _genres_field:
            parsed_genre = parse_genre(_genre_field)
            genres.append(parsed_genre)

    # COUNTRIES
    countries = []
    _countries_field = get_nested(film_data, "countries")
    if _countries_field:
        for _country_field in _countries_field:
            parsed_country = parse_country(_country_field)
            countries.append(parsed_country)

    # URLS
    trailer_stream_url = get_nested(film_data, "mainTrailer.streamUrl")
    trailer_youtube = get_nested(film_data, "mainTrailer.sourceVideoUrl")

    _cover_pre_url = get_nested(film_data, "cover.image.avatarsUrl")
    cover_url = get_full_url(_cover_pre_url)

    # ACTORS
    actors = []
    _actors_field = get_nested(film_data, "actors")
    if _actors_field:
        _actors_items = get_nested(_actors_field, "items")
        for _actor_item in _actors_items:
            person_data = get_nested(_actor_item, "person")
            actors.append(parse_person_data(person_data))

    # VOICE OVER ACTORS
    voice_over_actors = []
    _voice_actors_field = get_nested(film_data, "voiceOverActors")
    if _voice_actors_field:
        _voice_over_actors_items = get_nested(_voice_actors_field, "items")
        for _voice_over_actor_item in _voice_over_actors_items:
            person_data = get_nested(_voice_over_actor_item, "person")
            voice_over_actors.append(parse_person_data(person_data))

    # TAGLINE
    tagline = get_nested(film_data, "tagline")

    # DIRECTORS
    directors = []
    _directors_field = get_nested(film_data, "directors")
    if _directors_field:
        _directors_items = get_nested(_directors_field, "items")
        for _director_item in _directors_items:
            person_data = get_nested(_director_item, "person")
            directors.append(parse_person_data(person_data))

    # TODO: ADD:
    #   - WRITERS
    #   - PRODUCERS
    #   - OPERATORS
    #   - COMPOSERS
    #   - BOX_OFFICE

    # POSTERS
    _poster_pre_url = get_nested(film_data, "poster.avatarsUrl")
    poster_url = get_full_url(_poster_pre_url)

    # RATINGS
    rating_imdb = get_nested(film_data, "rating.imdb.value")
    rating_kinopoisk = get_nested(film_data, "rating.kinopoisk.value")
    rating_kinopoisk_top10_pos = get_nested(film_data, "ratingLists.top10.position")
    rating_kinopoisk_top250_pos = get_nested(film_data, "ratingLists.top250.position")
    rating_russian_critics = get_nested(film_data, "rating.russianCritics.value")
    rating_world_wide_critics = get_nested(film_data, "rating.worldwideCritics.value")

    # DURATION & URL
    duration = get_nested(film_data, "duration")
    url = FILM_URL_TEMPLATE.format(id)

    # TODO: filmMainAward

    parsed_data = {
        "id": id,
        "title_russian": title_russian,
        "title_original": title_original,
        "production_year": production_year,
        "short_description": short_description,
        "synopsis": synopsis,
        "genres": genres,
        "countries": countries,
        "trailer_stream_url": trailer_stream_url,
        "trailer_youtube": trailer_youtube,
        "cover_url": cover_url,
        "actors": actors,
        "voice_over_actors": voice_over_actors,
        "tagline": tagline,
        "directors": directors,
        "poster_url": poster_url,
        "rating_imdb": rating_imdb,
        "rating_kinopoisk": rating_kinopoisk,
        "rating_kinopoisk_top10_pos": rating_kinopoisk_top10_pos,
        "rating_kinopoisk_top250_pos": rating_kinopoisk_top250_pos,
        "rating_russian_critics": rating_russian_critics,
        "rating_world_wide_critics": rating_world_wide_critics,
        "duration": duration,
        "url": url,
        "typename": typename,
    }

    return parsed_data


def parse_movie_data(movie_data: dict) -> dict:
    """
    Обобщающая функция для парсинга данных о фильмах и сериалах,
    вызывает parse_film_data или parse_tvseries_data в зависимости от типа данных.

    Parameters:
        movie_data (dict): Данные о фильме или сериале.

    Returns:
        dict: Обработанные данные о фильме или сериале.
    """

    typename = get_nested(movie_data, "__typename")
    typename = str(typename).lower()

    if typename == "film":
        return parse_film_data(movie_data)
    elif typename == "tvseries":
        return parse_tvseries_data(movie_data)
    elif typename == "miniseries":
        # TODO: ADD MINISERIES SUPPORT
        return {}
    elif typename == "video":
        # TODO: ADD VIDEO SUPPORT
        return {}

    else:
        raise ValueError(
            f"Error: parse_movie_data function got '__typename': {typename}, expected Film or TvSeries."
        )


def parse_trivia_data(trivia_data: dict) -> list[dict]:
    """
    Функция для парсинга блока данных с фактами о фильме или сериале.

    Parameters:
        trivia_data (dict): Данные о факте.

    Returns:
        dict: Обработанные данные о факте, содержащие ключ 'typename' со значением 'trivia'.
    """

    typename = get_nested(trivia_data, "__typename", required=True)
    typename = str(typename).lower()

    if typename != "trivia":
        raise ValueError(
            f"Error: process_trivia function got '__typename': '{typename}', expected 'Trivia'."
        )

    # BASE DATA
    id = get_nested(trivia_data, "id", required=True)
    is_spoiler = get_nested(trivia_data, "isSpoiler")
    text = get_nested(trivia_data, "text")
    trivia_type = get_nested(trivia_data, "type")
    trivia_type = str(trivia_type).lower()

    # TEXT MAY CONTAIN HTML SYNTAX. DELETING IT HERE.
    text = remove_html_tags(text)

    parsed_trivia_item = {
        "id": id,
        "is_spoiler": is_spoiler,
        "text": text,
        "trivia_type": trivia_type,
        "typename": typename,
    }

    return parsed_trivia_item


def parse_media_post_data(media_post_data: dict) -> list[dict]:
    """
    Функция для парсинга блока данных со статьями и постами о фильме или сериале.

    Parameters:
        media_post_data (dict): Данные о статье или посте.

    Returns:
        dict: Обработанные данные о статье или посте, содержащие ключ 'typename' со значением 'post'.
    """

    typename = get_nested(media_post_data, "__typename", required=True)
    typename = str(typename).lower()

    if typename != "post":
        raise ValueError(
            f"Error: parse_media_post_data function got '__typename': {typename}, expected 'Post'."
        )

    # BASE DATA
    id = get_nested(media_post_data, "id", required=True)
    title = get_nested(media_post_data, "title")
    _pre_published_at = get_nested(media_post_data, "publishedAt")
    _pre_published_at = datetime.strptime(_pre_published_at, "%Y-%m-%dT%H:%M:%SZ")
    published_at = _pre_published_at.strftime("%d.%m.%Y %H:%M:%S")

    # POST TYPE AND POSTER
    media_post_type = get_nested(media_post_data, "type")
    media_post_type = str(media_post_type).lower()
    poster_url = get_nested(media_post_data, "thumbImage.avatarsUrl")

    parsed_data = {
        "id": id,
        "title": title,
        "published_at": published_at,
        "media_post_type": media_post_type,
        "poster_url": poster_url,
        "typename": typename,
    }

    return parsed_data
