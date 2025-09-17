import asyncio
import unittest
from app import app
from unittest.mock import AsyncMock, patch
from litestar.testing import AsyncTestClient
from litestar.exceptions import HTTPException


class TestAPIDebug(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        app.debug = True

    def run_async(self, coro):
        return self.loop.run_until_complete(coro)

    # Тесты для /index
    def test_index_handler(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "app.render_main_debug_page", return_value="debug_main_page"
                ):
                    response = await client.get("/")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.text, "debug_main_page")

        self.run_async(async_test())

    # Тесты для /search
    def test_search_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_search", new_callable=AsyncMock
                ) as mock_search:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch(
                            "app.render_viewer_debug_page",
                            return_value="debug_template",
                        ):
                            mock_search.return_value = (
                                {"raw": "data"},
                                {"processed": "data"},
                            )
                            response = await client.get("/search?search_query=avatar")
                            self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    def test_search_handler_not_found(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_search", new_callable=AsyncMock
                ) as mock_search:
                    mock_search.return_value = None
                    response = await client.get("/search?search_query=2sfsj11id")
                    self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    def test_search_handler_empty_query(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                response = await client.get("/search?search_query=")
                self.assertEqual(response.status_code, 400)

        self.run_async(async_test())

    # Тесты для /info
    def test_info_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_info", new_callable=AsyncMock
                ) as mock_info:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch("app.validate_content_type"):
                            with patch(
                                "app.render_viewer_debug_page",
                                return_value="debug_template",
                            ):
                                mock_info.return_value = (
                                    {"raw": "info"},
                                    {"processed": "info_data"},
                                )
                                response = await client.get(
                                    "/info?content_type=film&id=1"
                                )
                                self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    def test_info_handler_invalid_content_type(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "app.validate_content_type",
                    side_effect=HTTPException(
                        status_code=415, detail="Invalid content type"
                    ),
                ):
                    response = await client.get("/info?content_type=invalid&id=1")
                    self.assertEqual(response.status_code, 415)

        self.run_async(async_test())

    def test_info_handler_not_found(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_info", new_callable=AsyncMock
                ) as mock_info:
                    with patch("app.validate_content_type"):
                        mock_info.return_value = None
                        response = await client.get(
                            "/info?content_type=film&id=121746127"
                        )
                        self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # Тесты для /similars
    def test_similars_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_similars", new_callable=AsyncMock
                ) as mock_similars:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch("app.validate_content_type"):
                            with patch(
                                "app.render_viewer_debug_page",
                                return_value="debug_template",
                            ):
                                mock_similars.return_value = (
                                    {"raw": "similars"},
                                    {"processed": "similars_data"},
                                )
                                response = await client.get(
                                    "/similars?content_type=film&id=1"
                                )
                                self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # Тесты для /person
    def test_person_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_person", new_callable=AsyncMock
                ) as mock_person:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch(
                            "app.render_viewer_debug_page",
                            return_value="debug_template",
                        ):
                            mock_person.return_value = (
                                {"raw": "person"},
                                {"processed": "person_data"},
                            )
                            response = await client.get("/person?id=3486150")
                            self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # Тесты для /trivias
    def test_trivias_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_trivias", new_callable=AsyncMock
                ) as mock_trivias:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch("app.validate_content_type"):
                            with patch(
                                "app.render_viewer_debug_page",
                                return_value="debug_template",
                            ):
                                mock_trivias.return_value = (
                                    {"raw": "trivias"},
                                    {"processed": "trivias_data"},
                                )
                                response = await client.get(
                                    "/trivias?content_type=film&id=2514"
                                )
                                self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    def test_trivias_handler_not_found_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_trivias", new_callable=AsyncMock
                ) as mock_trivias:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        with patch("app.validate_content_type"):
                            with patch(
                                "app.render_viewer_debug_page",
                                return_value="debug_template",
                            ):
                                mock_trivias.return_value = (
                                    {"raw": "trivias"},
                                    {"processed": "trivias_data"},
                                )
                                response = await client.get(
                                    "/trivias?content_type=film&id=1"
                                )
                                self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # Тесты для /media_posts
    def test_media_posts_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_media_posts", new_callable=AsyncMock
                ) as mock_posts:
                    with patch(
                        "app.render_viewer_debug_page", return_value="debug_template"
                    ):
                        mock_posts.return_value = (
                            {"raw": "posts"},
                            {"processed": "posts_data"},
                        )
                        response = await client.get(
                            "/media_posts?content_type=film&id=1"
                        )
                        self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # Тесты для /series_dates
    def test_series_dates_handler_success_debug(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.toramp.get_series_dates", new_callable=AsyncMock
                ) as mock_dates:
                    with patch(
                        "app.render_viewer_debug_page", return_value="debug_template"
                    ):
                        mock_dates.return_value = {"dates": "2023-01-01"}
                        response = await client.get("/series_dates?title=show")
                        self.assertEqual(response.status_code, 200)

        self.run_async(async_test())


if __name__ == "__main__":
    unittest.main()
