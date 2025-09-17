import re

from hubble.services.rutor.service_utils import clean_html, convert_to_full_torrent_url


def parse_rutor_html(html: str):
    """
    Извлекает из HTML-результатов следующие данные для каждой раздачи:
      - date: дата добавления (например, "27 Окт 24")
      - magnet: magnet-ссылка
      - torrent: относительная ссылка на торрент
      - title: название раздачи (текст ссылки)
      - size: размер раздачи (например, "16.48 GB")
      - seeds: количество сидов (int)
      - leechers: количество личей (int)

    Структура HTML может варьироваться (разное число колонок), поэтому:
      - дата берётся из первой TD,
      - блок с заголовком (с ссылками) – из второй TD,
      - размер – из предпоследней TD,
      - данные о пирах – из последней TD.
    Возвращает список словарей с чистыми данными.
    """
    results = []

    # Находим все строки с результатами (класс "gai" или "tum")
    rows = re.findall(
        r'<tr\s+class="(?:gai|tum)"[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE
    )
    for row in rows:
        # Извлекаем все содержимое ячеек <td>...</td> в строке
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL | re.IGNORECASE)
        if not tds or len(tds) < 3:
            continue

        # 1. Первая ячейка – дата
        date = clean_html(tds[0])

        # 2. Последняя TD содержит данные о пирах (сиды/личи)
        peers_html = tds[-1]
        peers_text = clean_html(peers_html)
        # Ищем все числа: первое – сиды, второе – личи
        numbers = re.findall(r"\d+", peers_text)
        seeds = int(numbers[0]) if numbers and len(numbers) >= 1 else 0
        leechers = int(numbers[1]) if numbers and len(numbers) >= 2 else 0

        # 3. Предпоследняя TD – размер раздачи
        size = clean_html(tds[-2])

        # 4. Блок с заголовком и ссылками – берем вторую TD (даже если есть colspan)
        title_block = tds[1]

        # Извлекаем все ссылки: ожидается, что:
        #   - первая ссылка (с классом "downgif") пропускается,
        #   - вторая содержит magnet-ссылку,
        #   - третья – торрент-ссылку и название.
        links = re.findall(
            r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            title_block,
            re.DOTALL | re.IGNORECASE,
        )
        magnet = ""
        torrent = ""
        title = ""
        if len(links) >= 3:
            magnet = links[1][0].strip()
            torrent = links[2][0].strip()
            title = clean_html(links[2][1])
        elif len(links) == 2:
            # на случай, если ссылка для скачивания отсутствует
            magnet = links[0][0].strip()
            torrent = convert_to_full_torrent_url(links[1][0].strip())
            title = clean_html(links[1][1])

        results.append(
            {
                "date": date,
                "magnet": magnet,
                "torrent": torrent,
                "title": title,
                "size": size,
                "seeds": seeds,
                "leechers": leechers,
            }
        )

    return results
