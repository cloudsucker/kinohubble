import aiohttp
from typing import Optional, Union

from hubble.services.rutor.parsers import parse_rutor_html
from hubble.services.rutor.service_utils import HEADERS, build_search_url


async def get_rutor_search(
    query: str,
    *,
    category: Optional[Union[str, int]] = None,
    mode: Optional[str] = None,
    scope: Optional[str] = None,
    sort: Optional[Union[str, int]] = None,
) -> str:
    """
    Асинхронно выполняет поиск на rutor.info.

    Параметры (передаются как именованные аргументы):
      - query: поисковая фраза.
      - category: одна из категорий (например, "any", "foreign_films", "music", "anime" и т.д.).
      - mode: режим поиска – "phrase", "all", "any" или "logic" (по умолчанию "all").
      - scope: область поиска – "title" (только название) или "both" (название и описание, по умолчанию "both").
      - sort: способ сортировки – "date_desc", "date_asc", "seeds_desc", "seeds_asc", "leechers_desc", "leechers_asc",
              "title_desc", "title_asc", "size_desc", "size_asc" или "relevance" (по умолчанию "date_desc").

    Если дополнительных параметров не задано, то формируется URL вида:
       BASE_URL/&lt;encoded_query&gt;
    Иначе URL выглядит как:
       BASE_URL/0/&lt;category_code&gt;/&lt;search_mode_code&gt;/&lt;sort_code&gt;/&lt;encoded_query&gt;

    Возвращает HTML-страницу с результатами поиска.
    """
    url = build_search_url(query, category=category, mode=mode, scope=scope, sort=sort)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response.raise_for_status()
    response_text = await response.text()
    if response_text:
        return parse_rutor_html(response_text)
    return {}
