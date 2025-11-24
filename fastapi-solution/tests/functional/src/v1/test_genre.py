import pytest


@pytest.mark.asyncio
class TestGenreDetails:
    """Тесты для деталей жанра по ID (API v1)"""

    async def test_get_genre_by_id(self, make_get_request, genres_test_data):
        """Получение жанра по ID"""
        genre = genres_test_data[0]
        genre_id = genre['id']

        response = await make_get_request(1, f'genres/{genre_id}')

        assert response['status'] == 200
        assert response['body']['id'] == str(genre_id)
        assert response['body']['name'] == genre['name']

    async def test_get_nonexistent_genre(self, make_get_request):
        """Запрос несуществующего жанра"""
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        response = await make_get_request(1, f'genres/{non_existent_uuid}')

        assert response['status'] == 404


@pytest.mark.asyncio
class TestGenreList:
    """Тесты для списка жанров (API v1)"""

    async def test_get_genre_list(self, make_get_request, genres_test_data):
        """Получить список жанров"""
        response = await make_get_request(1, 'genres/')

        assert response['status'] == 200
        assert len(response['body']) == len(genres_test_data)

        expected_ids = set(str(data['id']) for data in genres_test_data)
        received_ids = set(res['id'] for res in response['body'])
        assert received_ids == expected_ids

        for genre in response['body']:
            assert 'id' in genre
            assert 'name' in genre
