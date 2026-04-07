import pytest
import json
from redis.asyncio import Redis
from http import HTTPStatus

from content_api.internal.infrastructure.app_config import Settings
pytestmark = pytest.mark.asyncio


class TestCache:

    async def test_films_search_cache(self, make_get_request,
                                      test_settings: Settings):
        redis_url = f"redis://{test_settings.redis_host}:{test_settings.redis_port}"
        redis = Redis.from_url(redis_url)

        await redis.flushall()

        query_params = {'query': 'star', 'page': 1, 'per_page': 10}
        endpoint = 'films/search'

        response1 = await make_get_request(1, endpoint, query_params)
        assert response1['status'] == HTTPStatus.OK

        keys = await redis.keys("*")
        assert len(keys) > 0, "Ключ должен появиться в Redis после запроса"

        cache_value = await redis.get(keys[0])
        assert cache_value is not None

        cached_data = json.loads(cache_value)

        assert cached_data['total'] == response1['body']['total']
        assert len(cached_data['items']) == len(response1['body']['items'])

        response2 = await make_get_request(1, endpoint, query_params)
        assert response2['status'] == HTTPStatus.OK
        assert response1['body'] == response2['body']

        await redis.close()

    async def test_film_id_cache(self, make_get_request,
                                 test_settings: Settings, films_test_data):
        redis_url = f"redis://{test_settings.redis_host}:{test_settings.redis_port}"
        redis = Redis.from_url(redis_url)
        await redis.flushall()

        film = films_test_data[0]
        film_id = film['id']
        endpoint = f'films/{film_id}'

        response1 = await make_get_request(1, endpoint)
        assert response1['status'] == HTTPStatus.OK

        keys = await redis.keys("*")
        assert len(keys) > 0

        response2 = await make_get_request(1, endpoint)
        assert response2['body'] == response1['body']

        await redis.close()
