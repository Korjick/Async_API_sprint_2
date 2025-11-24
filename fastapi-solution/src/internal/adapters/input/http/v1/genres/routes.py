import uuid
from typing import List

from fastapi import APIRouter

from internal.adapters.input.http.v1.genres.schemas import GenreResponse
from internal.core.application.usecases.queries.genres.get_all_genres_query import (
    GetAllGenresHandlerProtocol,
    GetAllGenres,
)
from internal.core.application.usecases.queries.genres.get_genre_by_id_query import (
    GetGenreByIdHandlerProtocol,
    GetGenreById,
)


class GenreHandler:
    def __init__(
            self,
            get_all_genres: GetAllGenresHandlerProtocol,
            get_genre_by_id: GetGenreByIdHandlerProtocol,
    ):
        self.get_all_genres = get_all_genres
        self.get_genre_by_id = get_genre_by_id
        self.router = APIRouter(prefix='/genres', tags=['Жанры'])

        self.router.add_api_route(
            '/',
            self.genre_list,
            methods=["GET"],
            response_model=List[GenreResponse],
            summary="Получить список жанров",
        )
        self.router.add_api_route(
            '/{genre_id}',
            self.genre_detail,
            methods=["GET"],
            response_model=GenreResponse,
            summary="Получить жанр по id",
        )

    async def genre_list(self) -> List[GenreResponse]:
        """Получить список доступных жанров"""
        query = GetAllGenres()
        genres = await self.get_all_genres.handle(query)
        return [GenreResponse.from_domain(genre) for genre in genres]

    async def genre_detail(self, genre_id: uuid.UUID) -> GenreResponse:
        """Получить жанр по uuid"""
        query = GetGenreById(id=genre_id)
        genre = await self.get_genre_by_id.handle(query)
        return GenreResponse.from_domain(genre)
