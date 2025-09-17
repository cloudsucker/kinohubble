import json
from litestar.params import Parameter
from litestar.response import Template
from litestar.exceptions import HTTPException

from hubble.services.kinopoisk.service_utils import is_media_content_type_valid


# TEMPLATES FOR DEBUGGING
TEMPLATES_DIRECTORY = "hubble/debug_templates/"
DEBUG_MAIN_PAGE = "main_page.jinja2"
DEBUG_TEMPLATE = "viewer_page.jinja2"


# CONTENT TYPE KINOPOISK API VALIDATION
def validate_content_type(content_type: str) -> None:
    if not is_media_content_type_valid(content_type):
        raise HTTPException(
            status_code=415, detail=f"Invalid media content type: '{content_type}'"
        )


# PARAMETERS VALIDATION
ID = Parameter(int, gt=0, lt=99999999999)
CONTENT_TYPE = Parameter(str, min_length=1, max_length=30)
SEARCH_QUERY = Parameter(str, min_length=1, max_length=100)


# DEBUG PAGES RENDER FUNCTIONS
def render_main_debug_page() -> Template:
    return Template(template_name=DEBUG_MAIN_PAGE, media_type="text/html")


def render_viewer_debug_page(original_json, processed_json) -> Template:
    return Template(
        template_name=DEBUG_TEMPLATE,
        context={
            "original_json": json.dumps(original_json, ensure_ascii=False),
            "processed_json": json.dumps(processed_json, ensure_ascii=False),
        },
        media_type="text/html",
    )
