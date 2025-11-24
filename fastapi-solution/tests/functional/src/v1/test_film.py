import pytest
from internal.adapters.input.http.v1.films.schemas import FilmShortResponse


@pytest.mark.asyncio
class TestFilmsSearch:
    """Тесты для поиска фильмов (API v1)"""

    async def test_search_by_title(self, make_get_request):
        """Поиск фильма по названию"""
        response = await make_get_request(1, 'films/search',
                                          {'query': 'discovery'})

        assert response['status'] == 200
        assert len(response['body']['items']) > 0
        assert 'discovery' in response['body']['items'][0]['title'].lower()

    async def test_search_by_description(self, make_get_request):
        """Поиск фильма по описанию"""
        response = await make_get_request(1, 'films/search',
                                          {'query': 'Starfleet'})

        assert response['status'] == 200
        assert len(response['body']['items']) > 0

    async def test_search_no_result(self, make_get_request):
        """Поиск без результатов"""
        response = await make_get_request(1, 'films/search',
                                          {'query': 'CatchMeIfYouCan'})

        assert response['status'] == 200
        assert len(response['body']['items']) == 0
        assert response['body']['total'] == 0

    async def test_search_pagination(self, make_get_request):
        """Проверка пагинации в поиске"""
        response = await make_get_request(1, 'films/search', {'page': 2,
                                                              'per_page': 10,
                                                              'query': 'Test'})
        assert response['status'] == 200
        assert len(response['body']['items']) == 10
        assert response['body']['page'] == 2
        assert response['body']['per_page'] == 10


@pytest.mark.asyncio
class TestFilmsDetails:
    """Тесты для деталей фильма по ID (API v1)"""

    async def test_get_film_by_id(self, make_get_request, films_test_data):
        """Получение фильма по ID"""
        film = films_test_data[0]
        film_id = film['id']

        response = await make_get_request(1, f'films/{film_id}')

        assert response['status'] == 200
        assert response['body']['id'] == str(film_id)
        assert response['body']['title'] == film['title']

    async def test_get_nonexistent_film(self, make_get_request):
        """Запрос несуществующего фильма"""
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        response = await make_get_request(1, f'films/{non_existent_uuid}')

        assert response['status'] == 404
