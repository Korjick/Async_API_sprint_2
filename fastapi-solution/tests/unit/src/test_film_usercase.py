import uuid

import pytest
from unittest.mock import AsyncMock, Mock
from content_api.internal.pkg.pagination import PaginatedResult
from content_api.internal.pkg.errors import ObjectNotFoundError
from content_api.internal.core.domain.models.film import Film
from content_api.internal.ports.input.films.get_film_by_id_handler import \
    GetFilmById
from content_api.internal.ports.input.films.get_films_by_params_handler import \
    GetFilmsByParams
from content_api.internal.ports.output.films_repository import FilmSearchParams
from content_api.internal.core.application.usecases.queries.films.get_film_by_id_query import \
    GetFilmsByIdUseCase
from content_api.internal.core.application.usecases.queries.films.get_films_by_params_query import \
    GetFilmsByParamsUseCase


def _as_domain_film(raw: dict) -> Film:
    return Film(
        oid=uuid.UUID(str(raw["id"])),
        title=raw["title"],
        description=raw.get("description"),
        imdb_rating=raw.get("imdb_rating"),
        genres=raw.get("genres"),
        actors=raw.get("actors"),
        writers=raw.get("writers"),
        directors=raw.get("directors"),
    )


class TestGetFilmsUseCase:
    """Тесты для usecase фильмов"""

    @pytest.fixture
    def mock_film_repository(self):
        """Фикстура для мок-репозитория"""
        return Mock()

    @pytest.fixture
    def get_film_by_id_usecase(self, mock_film_repository):
        """Фикстура для usecase получения фильма по ID"""
        return GetFilmsByIdUseCase(film_repository=mock_film_repository)

    @pytest.fixture
    def get_films_by_params_usecase(self, mock_film_repository):
        """Фикстура для usecase получения фильмов по параметрам"""
        return GetFilmsByParamsUseCase(film_repository=mock_film_repository)

    @pytest.fixture
    def sample_film(self, films_test_data):
        """Фикстура для тестового фильма"""
        film_data = films_test_data[0]
        return _as_domain_film(film_data)

    @pytest.fixture
    def sample_paginated_result(self, films_test_data):
        """Фикстура для тестового пагинированного результата"""
        films = [_as_domain_film(film_data) for film_data in
                 films_test_data[:3]]
        return PaginatedResult(
            items=films,
            total=len(films_test_data),
            page=1,
            per_page=3
        )

    @pytest.mark.asyncio
    async def test_get_film_by_id_success(self, get_film_by_id_usecase,
                                          mock_film_repository,
                                          films_test_data):
        """
        Тест успешного получения фильма по ID
        """
        expected_film = films_test_data[0]
        expected_film_id = uuid.UUID(expected_film['id'])
        sample_film = _as_domain_film(expected_film)

        mock_film_repository.get_film_by_id = AsyncMock(
            return_value=sample_film)

        # Act (Действие)
        result = await get_film_by_id_usecase.handle(
            GetFilmById(id=expected_film_id))

        # Assert (Проверка)
        mock_film_repository.get_film_by_id.assert_called_once_with(
            expected_film_id)

        # Проверяем, что результат совпадает с ожидаемым
        assert result == sample_film
        assert result.id == expected_film_id
        assert result.title == expected_film['title']
        assert result.genres == expected_film['genres']
        assert result.directors == expected_film['directors']
        assert result.actors == expected_film['actors']
        assert result.writers == expected_film['writers']

    @pytest.mark.asyncio
    async def test_get_film_by_id_not_found(self, get_film_by_id_usecase,
                                            mock_film_repository):
        """
        Тест, когда фильм не найден
        """
        # Arrange
        test_id = "non-existent-id"
        mock_film_repository.get_film_by_id = AsyncMock(
            side_effect=ObjectNotFoundError(param_name='id', entity_id=test_id)
        )

        # Act
        with pytest.raises(ObjectNotFoundError) as exc_info:
            await get_film_by_id_usecase.handle(GetFilmById(id=test_id))

        mock_film_repository.get_film_by_id.assert_called_once_with(test_id)
        expected_msg = f"{ObjectNotFoundError._base_msg}: {test_id}"
        assert expected_msg == str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_films_by_params_success(self,
                                               get_films_by_params_usecase,
                                               mock_film_repository,
                                               sample_paginated_result):
        """
        Тест успешного получения фильмов по параметрам
        """
        # Arrange
        query = GetFilmsByParams(
            sort="imdb_rating",
            person="James Doohan",
            page=1,
            per_page=10
        )

        mock_film_repository.search_by_params = AsyncMock(
            return_value=sample_paginated_result
        )

        # Act
        result = await get_films_by_params_usecase.handle(query)

        # Assert
        # Проверяем, что репозиторий вызван с правильными параметрами
        mock_film_repository.search_by_params.assert_called_once()

        call_args = mock_film_repository.search_by_params.call_args[0][0]
        assert isinstance(call_args, FilmSearchParams)
        assert call_args.sort == "imdb_rating"
        assert call_args.person == "James Doohan"
        assert call_args.page == 1
        assert call_args.per_page == 10

        # Проверяем результат
        assert result == sample_paginated_result
        assert len(result.items) == len(sample_paginated_result.items)
        assert result.total == sample_paginated_result.total
        assert result.page == sample_paginated_result.page
        assert result.per_page == sample_paginated_result.per_page

    @pytest.mark.asyncio
    async def test_get_films_by_params_empty_result(self,
                                                    get_films_by_params_usecase,
                                                    mock_film_repository):
        """
        Тест получения пустого результата при поиске по параметрам
        """
        # Arrange
        query = GetFilmsByParams(
            sort="imdb_rating",
            genre="NonExistentGenre",
            page=1,
            per_page=10
        )

        empty_result = PaginatedResult(
            items=[],
            total=0,
            page=1,
            per_page=10
        )

        mock_film_repository.search_by_params = AsyncMock(
            return_value=empty_result
        )

        # Act
        result = await get_films_by_params_usecase.handle(query)

        # Assert
        mock_film_repository.search_by_params.assert_called_once()
        call_args = mock_film_repository.search_by_params.call_args[0][0]
        assert call_args.genre == "NonExistentGenre"

        assert result == empty_result
        assert len(result.items) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_films_by_params_with_only_sort(self,
                                                      get_films_by_params_usecase,
                                                      mock_film_repository,
                                                      sample_paginated_result):
        """
        Тест получения фильмов только с параметром сортировки
        """
        # Arrange
        query = GetFilmsByParams(sort="imdb_rating",
                                 page=1,
                                 per_page=10)

        mock_film_repository.search_by_params = AsyncMock(
            return_value=sample_paginated_result
        )

        # Act
        result = await get_films_by_params_usecase.handle(query)

        # Assert
        mock_film_repository.search_by_params.assert_called_once()
        call_args = mock_film_repository.search_by_params.call_args[0][0]
        assert call_args.sort == "imdb_rating"
        assert call_args.genre is None
        assert call_args.person is None

        assert result == sample_paginated_result
