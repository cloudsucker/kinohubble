from litestar.params import Parameter
from litestar.exceptions import HTTPException

from hubble.services.kinopoisk.service_utils import is_media_content_type_valid


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
