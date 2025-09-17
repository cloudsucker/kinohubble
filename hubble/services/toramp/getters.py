import aiohttp

from hubble.utils import get_nested
from hubble.services.toramp.parsers import parse_search, parse_series_dates
from hubble.services.toramp.service_utils import HEADERS, SEARCH_URL


async def get_search(query: str) -> dict:
    data = aiohttp.FormData()
    data.add_field("value", query)
    data.add_field("db", "2")

    try:
        async with aiohttp.request(
            "POST", SEARCH_URL, headers=HEADERS, data=data
        ) as response:
            response_data = await response.text(encoding="utf-8")
    except Exception as e:
        return {}

    parsed_data = {}
    if response_data:
        parsed_data = parse_search(response_data)

    return parsed_data


async def get_series_dates(query: str) -> dict:
    search_result = await get_search(query)
    if not search_result:
        return {}

    url_to_parse = get_nested(search_result, "url")
    if not url_to_parse:
        return {}

    try:
        async with aiohttp.request("GET", url_to_parse, headers=HEADERS) as response:
            response_data = await response.text(encoding="utf-8")
    except Exception as e:
        return {}

    parsed_data = {}
    if response_data:
        parsed_data = parse_series_dates(response_data)

    search_result.update(parsed_data)
    search_result["typename"] = "toramp_search"

    return search_result
