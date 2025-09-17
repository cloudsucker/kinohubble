import re
import urllib.parse
from typing import Optional, Union


BASE_URL = "https://rutor.info/search"


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "max-age=0",
    "cookie": "redir_ipv6=redir_ipv6",
    "host": "rutor.info",
    "referer": "https://rutor.info/",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
}


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&nbsp;", " ").strip()


def convert_to_full_torrent_url(torrent_url: str) -> str | None:
    match = re.search(r"/torrent/(\d+)", torrent_url)
    if match:
        torrent_id = match.group(1)
        return f"https://d.rutor.info/download/{torrent_id}"
    else:
        return None


def build_search_url(
    query: str,
    category: Optional[Union[str, int]] = None,
    mode: Optional[str] = None,
    scope: Optional[str] = None,
    sort: Optional[Union[str, int]] = None,
) -> str:
    """
    Формирует URL для поиска на rutor.info.

    Если не переданы дополнительные параметры (category, mode, scope, sort),
    то URL формируется как BASE_URL/&lt;query&gt;.

    Иначе используются следующие правила (при отсутствии значения подставляются дефолты):
      - category: по-умолчанию "any" (любая категория)
      - mode: по-умолчанию "all"
      - scope: по-умолчанию "both" (название и описание)
      - sort: по-умолчанию "date_desc"

    Внутри функция использует словари для преобразования понятных ключей в нужные коды.
    """
    # Если никаких параметров не задано – формируем упрощённый URL
    if category is None and mode is None and scope is None and sort is None:
        return f"{BASE_URL}/{urllib.parse.quote(query)}"

    # Словарь для категорий (2-й параметр)
    CATEGORY_MAP = {
        "any": 0,
        "foreign_films": 1,
        "music": 2,
        "other": 3,
        "foreign_series": 4,
        "our_films": 5,
        "tv": 6,
        "mult": 7,
        "games": 8,
        "software": 9,
        "anime": 10,
        "books": 11,
        "popular_science_films": 12,
        "sport_health": 13,
        "humor": 15,
        "household": 14,
        "our_series": 16,
        "foreign_releases": 17,
    }

    # Подставляем дефолтные значения, если какой-то параметр не задан
    if category is None:
        category = "any"
    if mode is None:
        mode = "all"
    if scope is None:
        scope = "both"
    if sort is None:
        sort = "date_desc"

    # Преобразуем категорию в числовой код, если передан в виде строки
    if isinstance(category, str):
        category_code = CATEGORY_MAP.get(category.lower(), 0)
    else:
        category_code = category

    # Формирование кода режима поиска (3-й параметр)
    mode_map = {"phrase": "0", "all": "1", "any": "2", "logic": "3"}
    scope_map = {"title": "0", "both": "1"}
    search_mode_code = (
        f"{mode_map.get(mode.lower(), '1')}{scope_map.get(scope.lower(), '1')}0"
    )

    # Словарь для сортировки (4-й параметр)
    sort_mapping = {
        "date_desc": 0,
        "date_asc": 1,
        "seeds_desc": 2,
        "seeds_asc": 3,
        "leechers_desc": 4,
        "leechers_asc": 5,
        "title_desc": 6,
        "title_asc": 7,
        "size_desc": 8,
        "size_asc": 9,
        "relevance": 10,
    }
    if isinstance(sort, str):
        sort_code = sort_mapping.get(sort.lower(), 0)
    else:
        sort_code = sort

    # Первый параметр всегда 0
    first_param = 0
    encoded_query = urllib.parse.quote(query)

    return f"{BASE_URL}/{first_param}/{category_code}/{search_mode_code}/{sort_code}/{encoded_query}"
