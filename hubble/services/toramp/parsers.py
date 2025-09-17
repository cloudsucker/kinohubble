from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict


def parse_search(response_data: str) -> dict:
    soup = BeautifulSoup(response_data, "html.parser")
    ul_results = soup.find("ul", {"data-global-search": "ul-results"})

    li = ul_results.find("li")
    a_tag = li.find("a", href=True)
    url_found = a_tag["href"]
    id = url_found.split("id=")[-1]

    img_tag = li.find("img", src=True)
    poster_url = img_tag["src"].replace("width82", "width360") if img_tag else None

    title_russian = None
    production_year = None
    title_span = li.find("span", class_="title")
    if title_span:
        i_tag = title_span.find("i")
        if i_tag:
            production_year = i_tag.get_text(strip=True).strip("()")
            i_tag.extract()
        title_russian = title_span.get_text(strip=True)

    typename = None
    type_span = li.find("span", class_="type")
    if type_span:
        typename = type_span.get_text(strip=True)

    parsed_data = {
        "id": id,
        "url": url_found,
        "poster_url": poster_url,
        "title_russian": title_russian,
        "production_year": production_year,
        "typename": typename,
    }

    return parsed_data


def parse_series_dates(response_data: str) -> dict:
    soup = BeautifulSoup(response_data, "html.parser")

    main_section = None
    for section in soup.find_all("section"):
        if section.find("h1") and section.find("div"):
            main_section = section.find("div")
            break

    # Логика определения is_next_season_in_prod:
    # Сначала проверяем, содержит ли текст слова, означающие, что сериал закрыт,
    # затем – фразы, указывающие на отсутствие нового сезона,
    # и только потом – признаки наличия нового сезона.
    if main_section:
        status_text = ""
        status_p = main_section.find("p", class_=lambda x: x and "mb_3" in x)
        if status_p:
            em_tag = status_p.find("em")
            if em_tag:
                status_text = em_tag.get_text(separator=" ", strip=True)
        lower_status = status_text.lower()
        if any(
            word in lower_status
            for word in ["закрыт", "завершён", "завершен", "закончен"]
        ):
            is_next_season_in_prod = False
        elif "не будет" in lower_status or "нет нового" in lower_status:
            is_next_season_in_prod = False
        elif "tba" in lower_status or "решается" in lower_status:
            is_next_season_in_prod = None
        elif "премьера" in lower_status or "Дата выхода" in lower_status:
            is_next_season_in_prod = True
        elif "выходит" in lower_status:
            is_next_season_in_prod = True
        else:
            is_next_season_in_prod = None

        time_tag = main_section.find("time")
        new_seria_date = (
            time_tag["datetime"]
            if (is_next_season_in_prod and time_tag and time_tag.has_attr("datetime"))
            else None
        )
    else:
        is_next_season_in_prod = None
        new_seria_date = None

    seasons_order = OrderedDict()
    tables = soup.find_all("table", class_=lambda x: x and "series_eps_table" in x)
    for table in tables:
        tbody = table.find("tbody")
        if not tbody:
            continue
        rows = tbody.find_all("tr")
        for tr in rows:
            episode_id = tr.get("id", "")
            if not episode_id.startswith("episode_"):
                continue
            # Формат id: "episode_X.Y" (X — исходный номер сезона, Y — номер эпизода)
            id_part = episode_id.split("_", 1)[-1]  # например, "5.1"
            parts = id_part.split(".")
            if len(parts) != 2:
                continue
            try:
                orig_season = int(parts[0])
                seria_num = int(parts[1])
            except ValueError:
                continue

            # Извлекаем названия эпизода
            tds = tr.find_all("td")
            title_russian = ""
            title_original = ""
            if len(tds) >= 2:
                ft_div = tds[1].find("div", class_="ft")
                if ft_div:
                    title_russian = ft_div.get_text(strip=True)
                c_g2_div = tds[1].find("div", class_="c_g2")
                if c_g2_div:
                    title_original = c_g2_div.get_text(strip=True)

            # Извлекаем дату выхода эпизода
            release_date = ""
            if len(tds) >= 3:
                time_tag = tds[2].find("time")
                if time_tag and time_tag.has_attr("datetime"):
                    release_date = time_tag["datetime"]

            episode = {
                "seria_num": seria_num,
                "title_russian": title_russian,
                "title_original": title_original,
                "release_date": release_date,
            }
            seasons_order.setdefault(orig_season, []).append(episode)

    # --- Определение минимальной даты выпуска для сезона ---
    def get_min_release_date(episodes):
        date_objs = []
        for ep in episodes:
            if ep["release_date"]:
                try:
                    dt = datetime.strptime(ep["release_date"], "%Y-%m-%d")
                    date_objs.append(dt)
                except Exception:
                    pass
        return min(date_objs) if date_objs else None

    season_list = []
    for orig_season, eps in seasons_order.items():
        min_date = get_min_release_date(eps)
        season_list.append((orig_season, eps, min_date))
    # Сортируем по минимальной дате выпуска, а если даты нет — используем datetime.max
    season_list.sort(key=lambda x: x[2] if x[2] is not None else datetime.max)

    # Перенумеровываем сезоны последовательно (начиная с 1) и сортируем эпизоды по номеру
    seasons_output = []
    for idx, (orig_season, eps, _) in enumerate(season_list, start=1):
        eps_sorted = sorted(eps, key=lambda ep: ep["seria_num"])
        seasons_output.append({"season_num": idx, "episodes": eps_sorted})
    seasons_count = len(seasons_output)

    # Формируем итоговый результат, добавляя полученные данные к результату поиска
    parsed_data = {
        "is_next_season_in_prod": is_next_season_in_prod,
        "new_seria_date": new_seria_date,
        "seasons": seasons_output,
        "seasons_count": seasons_count,
    }

    return parsed_data
