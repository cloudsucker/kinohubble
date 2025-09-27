from typing import Union
from litestar.response import Template
from litestar import Litestar, Response, get
from litestar.exceptions import NotFoundException
from hubble.services.kinopoisk import (
    get_search,
    get_info,
    get_similars,
    get_person,
    get_trivias,
    get_media_posts,
)
from hubble.services.toramp import get_series_dates

from app_utils import (
    ID,
    CONTENT_TYPE,
    SEARCH_QUERY,
    validate_content_type,
)


@get("/search")
async def search_handler(
    search_query: str = SEARCH_QUERY,
) -> Union[Template, dict]:

    search_result = await get_search(search_query)

    if not search_result:
        raise NotFoundException(extra={"search_query": search_query})

    return Response(content=search_result, media_type="application/json")


@get("/info")
async def info_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    founded_info = await get_info(content_type, id)

    if not founded_info:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    return Response(content=founded_info, media_type="application/json")


@get("/similars")
async def similars_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    similars = await get_similars(content_type, id)

    if not similars:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    return Response(content=similars, media_type="application/json")


@get("/person")
async def person_handler(id: int = ID) -> Union[Template, dict]:
    person_info = await get_person(id)

    if not person_info:
        raise NotFoundException(extra={"id": id})

    return Response(content=person_info, media_type="application/json")


@get("/trivias")
async def trivias_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    trivias = await get_trivias(content_type, id)

    if not trivias:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    return Response(content=trivias, media_type="application/json")


@get("/media_posts")
async def media_posts_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    media_posts = await get_media_posts(content_type, id)

    return Response(content=media_posts, media_type="application/json")


@get("/series_dates")
async def series_dates_handler(title: str = SEARCH_QUERY) -> dict:
    series_dates = await get_series_dates(title)
    return Response(content=series_dates, media_type="application/json")


app = Litestar(
    route_handlers=[
        search_handler,
        info_handler,
        similars_handler,
        person_handler,
        trivias_handler,
        media_posts_handler,
        series_dates_handler,
    ]
)
