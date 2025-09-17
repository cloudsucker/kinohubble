import asyncio
import unittest
from app import app
from unittest.mock import AsyncMock, patch
from litestar.testing import AsyncTestClient
from litestar.exceptions import HTTPException


class TestAPIProduction(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        app.debug = False  # Важное отличие

    def run_async(self, coro):
        return self.loop.run_until_complete(coro)

    # /index
    def test_index_handler(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                response = await client.get("/")
                self.assertEqual(response.status_code, 200)

        self.run_async(async_test())

    # /search
    def test_search_handler_success(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_search", new_callable=AsyncMock
                ) as mock_search:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        mock_search.return_value = {"processed": "data"}
                        response = await client.get("/search?search_query=avatar")
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(
                            response.headers["content-type"], "application/json"
                        )

        self.run_async(async_test())

    def test_search_handler_not_found(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_search", new_callable=AsyncMock
                ) as mock_search:
                    mock_search.return_value = None
                    response = await client.get("/search?search_query=2sfsj11id")
                    self.assertEqual(response.status_code, 404)

        self.run_async(async_test())

    def test_search_handler_empty_query(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                response = await client.get("/search?search_query=")
                self.assertEqual(response.status_code, 400)

        self.run_async(async_test())

    # /info
    def test_info_handler_success(self):
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
                            mock_info.return_value = {"processed": "info_data"}
                            response = await client.get(
                                "/info?content_type=film&id=2514"
                            )
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(
                                response.headers["content-type"], "application/json"
                            )

        self.run_async(async_test())

    def test_info_handler_invalid_content_type(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "app.validate_content_type",
                    side_effect=HTTPException(status_code=415),
                ):
                    response = await client.get("/info?content_type=invalid&id=2514")
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
                        response = await client.get("/info?content_type=film&id=1")
                        self.assertEqual(response.status_code, 404)

        self.run_async(async_test())

    # /similars
    def test_similars_handler_success(self):
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
                            mock_similars.return_value = {"processed": "similars_data"}
                            response = await client.get(
                                "/similars?content_type=film&id=2514"
                            )
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(
                                response.headers["content-type"], "application/json"
                            )

        self.run_async(async_test())

    # /person
    def test_person_handler_success(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_person", new_callable=AsyncMock
                ) as mock_person:
                    with patch(
                        "database.requests.setters.set_data_to_db_items",
                        new_callable=AsyncMock,
                    ):
                        mock_person.return_value = {"processed": "person_data"}
                        response = await client.get("/person?id=3486150")
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(
                            response.headers["content-type"], "application/json"
                        )

        self.run_async(async_test())

    # /trivias
    def test_trivias_handler_success(self):
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
                            mock_trivias.return_value = {"processed": "trivias_data"}
                            response = await client.get(
                                "/trivias?content_type=film&id=2514"
                            )
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(
                                response.headers["content-type"], "application/json"
                            )

        self.run_async(async_test())

    # /media_posts
    def test_media_posts_handler_success(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.kinopoisk.get_media_posts", new_callable=AsyncMock
                ) as mock_posts:
                    mock_posts.return_value = {"processed": "posts_data"}
                    response = await client.get("/media_posts?content_type=film&id=1")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.headers["content-type"], "application/json"
                    )

        self.run_async(async_test())

    # /series_dates
    def test_series_dates_handler_success(self):
        async def async_test():
            async with AsyncTestClient(app=app) as client:
                with patch(
                    "hubble.services.toramp.get_series_dates", new_callable=AsyncMock
                ) as mock_dates:
                    mock_dates.return_value = {"dates": "2023-01-01"}
                    response = await client.get("/series_dates?title=show")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.headers["content-type"], "application/json"
                    )

        self.run_async(async_test())


if __name__ == "__main__":
    unittest.main()
