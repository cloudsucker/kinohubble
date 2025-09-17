# **🧱 Структура проекта**

**Проект был разделён на 4 слоя:**

1. **API-HANDLERS LAYER** - слой обработчиков API-запросов;
2. **SERVICE LAYER** - сервисный слой с конкретными реализациями для сторонних API;
3. **DATA PROCESSORS LAYER** - слой форматирования и унифицирования данных;
4. **UTILITIES LAYER** - слой вспомогательных функций.

![Project Layers](schemes/layers.png)

## **1. API-Хендлеры (`app.py`)**

**Обработка API-запросов и вызов бизнес-логики.**

-   Принимает запрос и параметры
-   Вызывает функции сервисного слоя (`get_*` функции)
-   Возвращает JSON-ответ

#### 🔹 **Шаблон названия:** `*_handler`

✅ **Пример:**

```python
@get("/search")
async def search_handler(search_query: str = Parameter()) -> dict:
    return await get_search(search_query)
```

## **2. Сервисный слой (Геттеры) (`hubble/services/kinopoisk/getters.py`)**

Запросы к API используемых сервисов и обработка ответа (для каждого сервиса своя реализация).

#### 🔹 **Что делает:**

-   Формирует запрос к стороннему API, получает ответ
-   Вызывает процессор конкретного сервиса (`parse_*` функции) для обработки данных
-   Возвращает отформатированные данные

#### 🔹 **Шаблон названия:** `get_*`

✅ **Пример:**

```python
async def get_search(query: str, debug: bool = False) -> dict:
    response = await suggest_search_async(query)
    json_data = await response.json()
    json_root = await get_nested(json_data, "data.suggest.top")

    if json_root:
        parsed_data = {}
        match = await get_nested(json_root, "topResult.global")
        # ...

    return parsed_data
```

## **3. Процессоры данных (`hubble/services/kinopoisk/parsers.py`)**

Обрабатывает данные, полученные от стороннего API, выделяя только нужную информацию (для каждого запроса и сервиса также своя реализация).

#### 🔹 **Что делает:**

-   Парсит JSON-ответ
-   Отбирает нужные поля
-   Приводит данные к удобному формату

#### 🔹 **Шаблон названия:** `parse_*`

✅ **Пример:**

```python
async def parse_movie_data(movie_data: dict) -> dict:
    typename = await get_nested(movie_data, "__typename")
    if typename == "Film":
        return await parse_film_data(movie_data)
    elif typename == "TvSeries":
        return await parse_tvseries_data(movie_data)
    else:
        raise TypeError(f"Unknown movie type {typename}")
```

## **4. Вспомогательные функции (`hubble/services/kinopoisk/helpers.py`, `hubble/services/utils.py`)**

Утилитные функции, которые могут использоваться в разных частях кода.

-   `hubble/services/utils.py` - общие утилиты для всех сервисов.
-   `hubble/services/kinopoisk/helpers.py` - утилиты, специфичные для сервиса Кинопоиска.

#### 🔹 **Что делает:**

-   Преобразование форматов
-   Первичная обработка данных

✅ **Пример:**

```python
async def get_full_url(url: str):
    return "https:" + url + "/orig/" if url else None
```
