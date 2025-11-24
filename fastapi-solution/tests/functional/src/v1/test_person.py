import pytest


@pytest.mark.asyncio
class TestPersonDetails:
    """Тесты для деталей персоны по ID (API v1)"""

    async def test_get_person_by_id(self, make_get_request, persons_test_data):
        """Получение персоны по ID"""
        person = persons_test_data[0]
        person_id = person['id']

        response = await make_get_request(1, f'persons/{person_id}')

        assert response['status'] == 200
        assert response['body']['id'] == str(person_id)
        assert response['body']['full_name'] == person['full_name']
        assert 'films' in response['body']

    async def test_get_person_film_by_id(self, make_get_request):
        """Получение фильмов для персоны по ID"""
        person_id = "c883c2c6-d7a4-4001-8084-e2851904e91a"  # Nicholas Meyer

        response = await make_get_request(1, f'persons/{person_id}')

        assert response['status'] == 200
        films = response['body']['films']
        assert len(films) >= 1

        target_film = next(
            (
                f
                for f in films
                if f['id'] == "6e5cd268-8ce4-45f9-87d2-52f0f26edc9e"
            ),
            None,
        )
        assert target_film is not None
        assert 'director' in target_film['roles']

    async def test_get_nonexistent_person(self, make_get_request):
        """Запрос несуществующей персоны"""
        uuid_val = "00000000-0000-0000-0000-000000000000"
        response = await make_get_request(1, f'persons/{uuid_val}')

        assert response['status'] == 404


@pytest.mark.asyncio
class TestPersonSearch:
    """Тесты для поиска персон по имени (API v1)"""

    async def test_get_person_by_fullname(self, make_get_request):
        """Поиск персон по имени"""
        response = await make_get_request(1, 'persons/search',
                                          {'query': 'William'})

        assert response['status'] == 200
        assert len(response['body']['items']) >= 3
        for person in response['body']['items']:
            assert 'id' in person
            assert 'full_name' in person
            assert 'films' in person

    async def test_get_film_by_person_fullname(self, make_get_request):
        """Получение фильма по имени персоны"""
        response = await make_get_request(1, 'persons/search',
                                          {'query': 'LeVar'})

        assert response['status'] == 200
        items = response['body']['items']
        assert len(items) > 0

        person = items[0]
        film = person['films'][0]
        assert film['id'] == 'b1384a92-f7fe-476b-b90b-6cec2b7a0dce'
        assert 'actor' in film['roles']

    async def test_nonexistent_fullname(self, make_get_request):
        """Поиск по несуществующему имени"""
        response = await make_get_request(1, 'persons/search',
                                          {'query': 'SomeIncognito'})

        assert response['status'] == 200
        assert len(response['body']['items']) == 0

    async def test_empty_string_query(self, make_get_request):
        """Пустая строка в запросе"""
        response = await make_get_request(1, 'persons/search', {'query': ''})

        # FastAPI валидирует min_length=1 и вернёт 422
        assert response['status'] == 422


@pytest.mark.asyncio
class TestPersonFilmEndpoint:
    """Тесты для /persons/{id}/film (фильмы по персоне)"""

    async def test_get_films_endpoint(self, make_get_request):
        # Leonard Nimoy (5a3d...)
        person_id = "5a3d0299-2df2-4070-9fda-65ff4dfa863c"
        response = await make_get_request(1, f'persons/{person_id}/film')

        assert response['status'] == 200
        assert len(response['body']) == 2

        titles = [f['title'] for f in response['body']]
        assert "The Wrath of Khan" in titles
        assert "The Search for Spock" in titles

    async def test_get_films_nonexistent_person(self, make_get_request):
        uuid_val = "00000000-0000-0000-0000-000000000000"
        response = await make_get_request(1, f'persons/{uuid_val}/film')

        assert response['status'] == 404
