import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from elasticsearch import AsyncElasticsearch, BadRequestError
from elasticsearch.helpers import async_bulk
from testcontainers.elasticsearch import ElasticSearchContainer
from testcontainers.redis import RedisContainer

from command.app.main import create_app
from functional.testdata.films_data import films_data
from functional.testdata.genres_data import genres_data
from functional.testdata.persons_data import persons_data
from internal.infrastructure.app_config import Settings


@pytest.fixture(scope='session')
def es_container():
    container = (
        ElasticSearchContainer("elasticsearch:8.19.7")
        .with_env("xpack.security.enabled", "false")
        .with_env("discovery.type", "single-node")
        .with_env("ES_JAVA_OPTS", "-Xms512m -Xmx512m")
    )
    with container as es:
        yield es


@pytest.fixture(scope='session')
def redis_container():
    with RedisContainer("redis:8.2.2-alpine") as redis:
        yield redis


@pytest.fixture(scope='session')
def test_settings(es_container, redis_container):
    """Настройки, указывающие на порты тестконтейнеров"""
    return Settings.model_validate(
        {
            "PROJECT_NAME": "test_project",
            "REDIS_HOST": redis_container.get_container_host_ip(),
            "REDIS_PORT": redis_container.get_exposed_port(6379),
            "ELASTIC_HOST": es_container.get_container_host_ip(),
            "ELASTIC_PORT": es_container.get_exposed_port(9200),
            "ELASTIC_SCHEMA": "http://",
        }
    )


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client(test_settings):
    url = f"{test_settings.elastic_schema}{test_settings.elastic_host}:{test_settings.elastic_port}"
    client = AsyncElasticsearch(hosts=url, verify_certs=False)
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_database(es_client):
    """Создание индексов и загрузка данных перед тестами"""
    data_map = [
        ('movies', films_data),
        ('genres', genres_data),
        ('persons', persons_data)
    ]

    for index_name, data in data_map:
        try:
            exists = await es_client.indices.exists(index=index_name)
        except BadRequestError:
            # В некоторых окружениях HEAD /{index} может вернуть 400,
            # считаем, что индекс просто ещё не существует.
            exists = False

        if exists:
            try:
                await es_client.indices.delete(index=index_name)
            except BadRequestError:
                # Игнорируем ошибки удаления, если индекс в процессе создания/удаления
                pass

        await es_client.indices.create(index=index_name)

        bulk_data = []
        for row in data:
            doc = row.copy()
            bulk_data.append({
                '_index': index_name,
                '_id': str(doc['id']),
                '_source': doc
            })

        if bulk_data:
            await async_bulk(client=es_client, actions=bulk_data)

        await es_client.indices.refresh(index=index_name)


@pytest_asyncio.fixture(scope='function')
async def fastapi_app(test_settings):
    app = create_app(settings=test_settings)
    return app


@pytest_asyncio.fixture(scope='function')
async def make_get_request(fastapi_app):
    """
    HTTP-клиент для тестов.
    Принимает (version, endpoint, params).
    Пример: await make_get_request(1, 'films/search', {...})
    """
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport,
                           base_url="http://test") as client:
        async def inner(version: int, endpoint: str, params: dict = None):
            url = f"/api/v{version}/{endpoint}"
            response = await client.get(url, params=params)
            return {
                'status': response.status_code,
                'body': response.json() if response.content else None,
                'headers': response.headers
            }

        yield inner


@pytest.fixture
def films_test_data():
    return films_data


@pytest.fixture
def genres_test_data():
    return genres_data


@pytest.fixture
def persons_test_data():
    return persons_data
