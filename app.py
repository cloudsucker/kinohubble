from typing import Union
from litestar.response import Template
from litestar.openapi import OpenAPIConfig
from litestar import Litestar, Response, get
from litestar.exceptions import NotFoundException
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from hubble.services.kinopoisk import (
    get_search,
    get_info,
    get_similars,
    get_person,
    get_trivias,
    get_media_posts,
)
from hubble.services.toramp import get_series_dates

from database._init_db import init_db
from database.requests.setters import set_data_to_db_items

from app_utils import (
    ID,
    CONTENT_TYPE,
    SEARCH_QUERY,
    TEMPLATES_DIRECTORY,
    validate_content_type,
    render_main_debug_page,
    render_viewer_debug_page,
)


async def startup():
    pass
    # await init_db()


@get("/")
async def index_handler() -> str:
    return render_main_debug_page()


@get("/search")
async def search_handler(
    search_query: str = SEARCH_QUERY,
) -> Union[Template, dict]:

    search_result = await get_search(search_query, debug=app.debug)

    if app.debug:
        original_json, processed_json = search_result
        # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(
            original_json, processed_json if processed_json else {"error": "404"}
        )

    if not search_result:
        print("wtf")
        raise NotFoundException(extra={"search_query": search_query})

    # await set_data_to_db_items(search_result)
    return Response(content=search_result, media_type="application/json")


@get("/info")
async def info_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    founded_info = await get_info(content_type, id, app.debug)

    if app.debug:
        original_json = founded_info[0]
        processed_json = founded_info[1] if founded_info[1] else {"error": "404"}
        # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(original_json, processed_json)

    if not founded_info:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    # await set_data_to_db_items(founded_info)
    return Response(content=founded_info, media_type="application/json")


@get("/similars")
async def similars_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    similars = await get_similars(content_type, id, debug=app.debug)

    if app.debug:
        original_json = similars[0]
        processed_json = similars[1] if similars[1] else {"error": "404"}
        # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(original_json, processed_json)

    if not similars:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    # await set_data_to_db_items(similars)
    return Response(content=similars, media_type="application/json")


@get("/person")
async def person_handler(id: int = ID) -> Union[Template, dict]:
    person_info = await get_person(id, app.debug)

    import pprint

    pprint.pprint(person_info)

    if app.debug:
        original_json = person_info[0]
        processed_json = person_info[1] if person_info[1] else {"error": "404"}
        # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(original_json, processed_json)

    if not person_info:
        raise NotFoundException(extra={"id": id})

    # await set_data_to_db_items(person_info)
    return Response(content=person_info, media_type="application/json")


@get("/trivias")
async def trivias_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    trivias = await get_trivias(content_type, id, app.debug)

    if app.debug:
        original_json = trivias[0]
        processed_json = trivias[1]
        # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(original_json, processed_json)

    if not trivias:
        raise NotFoundException(extra={"content_type": content_type, "id": id})

    # await set_data_to_db_items(trivias)
    return Response(content=trivias, media_type="application/json")


@get("/media_posts")
async def media_posts_handler(
    content_type: str = CONTENT_TYPE, id: int = ID
) -> Union[Template, dict]:

    validate_content_type(content_type)
    media_posts = await get_media_posts(content_type, id, app.debug)

    if app.debug:
        original_json = media_posts[0]
        processed_json = media_posts[1]
        # TODO: ADD MEDIA POSTS SUPPORT IN DATABASE
        # # await set_data_to_db_items(processed_json)
        return render_viewer_debug_page(original_json, processed_json)

    # TODO: ADD MEDIA POSTS SUPPORT IN DATABASE
    # await set_data_to_db_items(media_posts)
    return Response(content=media_posts, media_type="application/json")


@get("/series_dates")
async def series_dates_handler(title: str = SEARCH_QUERY) -> dict:

    series_dates = await get_series_dates(title)
    if app.debug:
        return render_viewer_debug_page(
            {"note": "html pages is not supported yet"}, series_dates
        )
    return Response(content=series_dates, media_type="application/json")


# START: uvicorn app:app --host 127.0.0.1 --port 8080 --reload
app = Litestar(
    route_handlers=[
        index_handler,
        search_handler,
        info_handler,
        similars_handler,
        person_handler,
        trivias_handler,
        media_posts_handler,
        series_dates_handler,
    ],
    template_config=TemplateConfig(
        directory=TEMPLATES_DIRECTORY, engine=JinjaTemplateEngine
    ),
    openapi_config=OpenAPIConfig(title="Hubble API", version="1.0.0", path="/openapi"),
    on_startup=[startup],
)
