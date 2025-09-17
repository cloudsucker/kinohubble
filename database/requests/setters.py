from datetime import datetime
from sqlalchemy import select

from hubble.utils import get_nested
from database.db import AsyncSessionLocal
from database.models import Person, Film, TvSeries, Genre, Country, Role, Trivia


UNIQUE_FIELDS = {
    Person: ("kinopoisk_id",),
    Film: ("kinopoisk_id",),
    TvSeries: ("kinopoisk_id",),
    Genre: ("kinopoisk_id",),
    Country: ("name",),
    Role: ("name",),
    Trivia: ("kinopoisk_id",),
}


async def resolve_duplicates(obj, session, visited=None):
    """
    Рекурсивно обходит объект и его отношения, пытаясь найти в БД уже существующие записи
    по заданным уникальным полям. Если объект найден, присваивает найденный primary key.
    Для предотвращения бесконечной рекурсии используется множество visited.
    """
    if visited is None:
        visited = set()
    if id(obj) in visited:
        return obj
    visited.add(id(obj))

    model_class = type(obj)
    if model_class in UNIQUE_FIELDS:
        fields = UNIQUE_FIELDS[model_class]
        conditions = [
            getattr(model_class, field) == getattr(obj, field) for field in fields
        ]
        stmt = select(model_class).filter(*conditions)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            obj.id = existing.id

    # Обрабатываем все отношения рекурсивно
    for rel in obj.__mapper__.relationships:
        related = getattr(obj, rel.key)
        if related is None:
            continue
        if rel.uselist:
            resolved_list = []
            for item in related:
                resolved_item = await resolve_duplicates(item, session, visited)
                resolved_list.append(resolved_item)
            setattr(obj, rel.key, resolved_list)
        else:
            resolved_item = await resolve_duplicates(related, session, visited)
            setattr(obj, rel.key, resolved_item)
    return obj


# Функции для создания объектов верхнего уровня:


async def set_person(person_data: dict) -> Person:
    typename = get_nested(person_data, "typename", required=True)
    if typename != "person":
        raise ValueError(
            f"{set_person.__qualname__}: Ожидался тип 'person', получен {typename}"
        )
    pid = get_nested(person_data, "id", required=True)
    name = get_nested(person_data, "name")
    original_name = get_nested(person_data, "original_name")
    birth_date_str = get_nested(person_data, "birth_date")
    birth_date = _parse_date(birth_date_str) if birth_date_str else None
    avatars_url = get_nested(person_data, "avatars_url")
    person_url = get_nested(person_data, "person_url")
    person = Person(
        kinopoisk_id=pid,
        name=name,
        original_name=original_name,
        birth_date=birth_date,
        kinopoisk_avatars_url=avatars_url,
        kinopoisk_person_url=person_url,
    )
    roles = get_nested(person_data, "roles")
    if roles:
        for role_name in roles:
            role_obj = await set_role(role_name)
            person.roles.append(role_obj)
    return person


async def set_role(role_name: str) -> Role:
    if not role_name:
        raise ValueError(f"{set_role.__qualname__}: Имя роли не может быть пустым")
    return Role(name=role_name)


async def set_film(film_data: dict) -> Film:
    typename = get_nested(film_data, "typename", required=True)
    if typename != "film":
        raise ValueError(
            f"{set_film.__qualname__}: Ожидался тип 'film', получен {typename}"
        )
    fid = get_nested(film_data, "id", required=True)
    title_russian = get_nested(film_data, "title_russian")
    title_original = get_nested(film_data, "title_original")
    production_year = get_nested(film_data, "production_year")
    short_description = get_nested(film_data, "short_description")
    synopsis = get_nested(film_data, "synopsis")
    trailer_ya_stream_url = get_nested(film_data, "trailer_stream_url")
    trailer_youtube = get_nested(film_data, "trailer_youtube")
    cover_url = get_nested(film_data, "cover_url")
    tagline = get_nested(film_data, "tagline")
    kinopoisk_poster_url = get_nested(film_data, "kinopoisk_poster_url")
    rating_imdb = get_nested(film_data, "rating_imdb")
    rating_kinopoisk = get_nested(film_data, "rating_kinopoisk")
    rating_kinopoisk_top10_pos = get_nested(film_data, "rating_kinopoisk_top10_pos")
    rating_kinopoisk_top250_pos = get_nested(film_data, "rating_kinopoisk_top250_pos")
    rating_russian_critics = get_nested(film_data, "rating_russian_critics")
    rating_world_wide_critics = get_nested(film_data, "rating_world_wide_critics")
    duration = get_nested(film_data, "duration")
    kinopoisk_url = get_nested(film_data, "url")
    film = Film(
        kinopoisk_id=fid,
        title_russian=title_russian,
        title_original=title_original,
        production_year=production_year,
        short_description=short_description,
        synopsis=synopsis,
        trailer_ya_stream_url=trailer_ya_stream_url,
        trailer_youtube=trailer_youtube,
        cover_url=cover_url,
        tagline=tagline,
        kinopoisk_poster_url=kinopoisk_poster_url,
        rating_imdb=rating_imdb,
        rating_kinopoisk=rating_kinopoisk,
        rating_kinopoisk_top10_pos=rating_kinopoisk_top10_pos,
        rating_kinopoisk_top250_pos=rating_kinopoisk_top250_pos,
        rating_russian_critics=rating_russian_critics,
        rating_world_wide_critics=rating_world_wide_critics,
        duration=duration,
        kinopoisk_url=kinopoisk_url,
    )
    # Вложенные объекты
    actors = get_nested(film_data, "actors")
    if actors:
        for actor_data in actors:
            film.actors.append(await set_person(actor_data))
    directors = get_nested(film_data, "directors")
    if directors:
        for director_data in directors:
            film.directors.append(await set_person(director_data))
    voice_over_actors = get_nested(film_data, "voice_over_actors")
    if voice_over_actors:
        for va_data in voice_over_actors:
            film.voice_over_actors.append(await set_person(va_data))
    genres = get_nested(film_data, "genres")
    if genres:
        for genre_data in genres:
            film.genres.append(await set_genre(genre_data))
    countries = get_nested(film_data, "countries")
    if countries:
        for country_data in countries:
            film.countries.append(await set_country(country_data))
    return film


async def set_tvseries(tvseries_data: dict) -> TvSeries:
    typename = get_nested(tvseries_data, "typename", required=True)
    if typename != "tvseries":
        raise ValueError(
            f"{set_tvseries.__qualname__}: Ожидался тип 'tvseries', получен {typename}"
        )
    tid = get_nested(tvseries_data, "id", required=True)
    title_russian = get_nested(tvseries_data, "title_russian")
    title_original = get_nested(tvseries_data, "title_original")
    production_year = get_nested(tvseries_data, "production_year")
    short_description = get_nested(tvseries_data, "short_description")
    synopsis = get_nested(tvseries_data, "synopsis")
    release_start = get_nested(tvseries_data, "release_start")
    release_end = get_nested(tvseries_data, "release_end")
    seasons_count = get_nested(tvseries_data, "seasons_count")
    cover_url = get_nested(tvseries_data, "cover_url")
    trailer_ya_stream_url = get_nested(tvseries_data, "trailer_stream_url")
    trailer_youtube = get_nested(tvseries_data, "trailer_youtube")
    tagline = get_nested(tvseries_data, "tagline")
    kinopoisk_poster_url = get_nested(tvseries_data, "kinopoisk_poster_url")
    rating_imdb = get_nested(tvseries_data, "rating_imdb")
    rating_kinopoisk = get_nested(tvseries_data, "rating_kinopoisk")
    rating_kinopoisk_top10_pos = get_nested(tvseries_data, "rating_kinopoisk_top10_pos")
    rating_kinopoisk_top250_pos = get_nested(
        tvseries_data, "rating_kinopoisk_top250_pos"
    )
    rating_russian_critics = get_nested(tvseries_data, "rating_russian_critics")
    rating_worldwide_critics = get_nested(tvseries_data, "rating_worldwide_critics")
    duration_total = get_nested(tvseries_data, "duration_total")
    duration_series = get_nested(tvseries_data, "duration_series")
    kinopoisk_url = get_nested(tvseries_data, "url")
    tvseries = TvSeries(
        kinopoisk_id=tid,
        title_russian=title_russian,
        title_original=title_original,
        production_year=production_year,
        short_description=short_description,
        synopsis=synopsis,
        release_start=release_start,
        release_end=release_end,
        seasons_count=seasons_count,
        cover_url=cover_url,
        trailer_ya_stream_url=trailer_ya_stream_url,
        trailer_youtube=trailer_youtube,
        tagline=tagline,
        kinopoisk_poster_url=kinopoisk_poster_url,
        rating_imdb=rating_imdb,
        rating_kinopoisk=rating_kinopoisk,
        rating_kinopoisk_top10_pos=rating_kinopoisk_top10_pos,
        rating_kinopoisk_top250_pos=rating_kinopoisk_top250_pos,
        rating_russian_critics=rating_russian_critics,
        rating_world_wide_critics=rating_worldwide_critics,
        duration_total=duration_total,
        duration_series=duration_series,
        kinopoisk_url=kinopoisk_url,
    )
    actors = get_nested(tvseries_data, "actors")
    if actors:
        for actor_data in actors:
            tvseries.actors.append(await set_person(actor_data))
    voice_over_actors = get_nested(tvseries_data, "voice_over_actors")
    if voice_over_actors:
        for va_data in voice_over_actors:
            tvseries.voice_over_actors.append(await set_person(va_data))
    directors = get_nested(tvseries_data, "directors")
    if directors:
        for director_data in directors:
            tvseries.directors.append(await set_person(director_data))
    genres = get_nested(tvseries_data, "genres")
    if genres:
        for genre_data in genres:
            tvseries.genres.append(await set_genre(genre_data))
    countries = get_nested(tvseries_data, "countries")
    if countries:
        for country_data in countries:
            tvseries.countries.append(await set_country(country_data))
    return tvseries


async def set_genre(genre_data: dict) -> Genre:
    typename = get_nested(genre_data, "typename", required=True)
    if typename != "genre":
        raise ValueError(
            f"{set_genre.__qualname__}: Ожидался тип 'genre', получен {typename}"
        )
    gid = get_nested(genre_data, "id", required=True)
    name = get_nested(genre_data, "name", required=True)
    slug = get_nested(genre_data, "slug")
    return Genre(kinopoisk_id=gid, name=name, slug=slug)


async def set_country(country_data: dict) -> Country:
    typename = get_nested(country_data, "typename", required=True)
    if typename != "country":
        raise ValueError(
            f"{set_country.__qualname__}: Ожидался тип 'country', получен {typename}"
        )
    cid = get_nested(country_data, "id", required=True)
    name = get_nested(country_data, "name", required=True)
    return Country(kinopoisk_id=cid, name=name)


async def set_trivia(trivia_data: dict) -> Trivia:
    typename = get_nested(trivia_data, "typename", required=True)
    if typename != "trivia":
        raise ValueError(
            f"{set_trivia.__qualname__}: Ожидался тип 'trivia', получен {typename}"
        )
    tid = get_nested(trivia_data, "id", required=True)
    text = get_nested(trivia_data, "text", required=True)
    trivia_type = get_nested(trivia_data, "trivia_type", required=True)
    return Trivia(kinopoisk_id=tid, text=text, trivia_type=trivia_type)


def _parse_date(date_str: str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


# Функция для обработки объектов типа search_result
async def set_search_result(search_data: dict) -> dict:
    stype = get_nested(search_data, "typename", required=True)
    if stype != "search_result":
        raise ValueError(f"Ожидался тип 'search_result', получен {stype}")
    result = {}

    # Обрабатываем match – одиночный объект (film, tvseries или person)
    match_data = search_data.get("match")
    if match_data:
        mtype = get_nested(match_data, "typename", required=True)
        if mtype.lower() in ("film", "movie"):
            result["match"] = await set_film(match_data)
        elif mtype.lower() == "tvseries":
            result["match"] = await set_tvseries(match_data)
        elif mtype.lower() == "person":
            result["match"] = await set_person(match_data)
        else:
            result["match"] = None
    else:
        result["match"] = None

    # Обрабатываем movies – список объектов (film или tvseries)
    movies_data = search_data.get("movies")
    processed_movies = []
    if movies_data and isinstance(movies_data, list):
        for item in movies_data:
            # Если элемент обёрнут в ключ "movie", берём его
            movie_data = get_nested(item, "movie") if "movie" in item else item
            mtype = get_nested(movie_data, "typename", required=True)
            if mtype.lower() in ("film", "movie"):
                processed_movies.append(await set_film(movie_data))
            elif mtype.lower() == "tvseries":
                processed_movies.append(await set_tvseries(movie_data))
    result["movies"] = processed_movies

    # Обрабатываем persons – список объектов person
    persons_data = search_data.get("persons")
    processed_persons = []
    if persons_data and isinstance(persons_data, list):
        for item in persons_data:
            person_data = get_nested(item, "person") if "person" in item else item
            processed_persons.append(await set_person(person_data))
    result["persons"] = processed_persons

    # cinemas и movie_lists пропускаем (не обрабатываем)
    result["cinemas"] = search_data.get("cinemas")
    result["movie_lists"] = search_data.get("movie_lists")
    result["typename"] = "search_result"

    return result


# Функция сохранения объекта (или нескольких) в базу данных с обновлением, если запись уже существует.
# Если получен словарь (например, для search_result), то сохраняем каждое значение отдельно.
async def save_object(obj):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await resolve_duplicates(obj, session)
            merged_obj = await session.merge(obj)
        await session.commit()
        await session.refresh(merged_obj)
    return merged_obj


async def save_objects(objs: list) -> list:
    result = []
    for obj in objs:
        result.append(await save_object(obj))
    return result


# Основная функция, создающая объект(ы) нужного типа и сохраняющая(ие) его(их) в базу данных
async def set_data_to_db_items(data: dict | list):

    if isinstance(data, dict):
        if not data or data.get("error"):
            return

    if isinstance(data, list):
        saved_objects = []
        for item in data:
            saved_objects.append(await set_data_to_db_items(item))
        return saved_objects

    typename = get_nested(data, "typename", required=True)
    if typename == "film":
        obj = await set_film(data)
        return await save_object(obj)
    elif typename == "tvseries":
        obj = await set_tvseries(data)
        return await save_object(obj)
    elif typename == "person":
        obj = await set_person(data)
        return await save_object(obj)
    elif typename == "genre":
        obj = await set_genre(data)
        return await save_object(obj)
    elif typename == "country":
        obj = await set_country(data)
        return await save_object(obj)
    elif typename == "trivia":
        obj = await set_trivia(data)
        return await save_object(obj)
    elif typename == "search_result":
        search_result = await set_search_result(data)
        if search_result.get("match"):
            search_result["match"] = await save_object(search_result["match"])
        if search_result.get("movies"):
            search_result["movies"] = await save_objects(search_result["movies"])
        if search_result.get("persons"):
            search_result["persons"] = await save_objects(search_result["persons"])
        return search_result
    else:
        raise ValueError(
            f"{set_data_to_db_items.__qualname__}: Неизвестный typename: {typename}"
        )
