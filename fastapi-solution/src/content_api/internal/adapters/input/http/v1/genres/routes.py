import uuid
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends

from content_api.internal.adapters.input.http.v1.genres.schemas import GenreResponse
from content_api.internal.ports.input.genres.get_all_genres_handler import \
    AllGenresHandlerProtocol, get_instance as all_genres_handler, GetAllGenres
from content_api.internal.ports.input.genres.get_genre_by_id_handler import \
    GenreByIdHandlerProtocol, get_instance as genre_by_id_handler, GetGenreById
from content_api.internal.adapters.input.http.dependencies import optional_auth_identity
from content_api.internal.ports.output.auth_verifier import AuthUserIdentity

router = APIRouter(prefix='/genres', tags=['Жанры'])


@router.get("/",
            response_model=List[GenreResponse],
            summary="Получить список жанров")
async def genre_list(
        all_genres: Annotated[
            AllGenresHandlerProtocol, Depends(all_genres_handler)],
        _auth_user: Annotated[Optional[AuthUserIdentity], Depends(optional_auth_identity)]) \
        -> List[GenreResponse]:
    query = GetAllGenres()
    genres = await all_genres.handle(query)
    return [GenreResponse.from_domain(genre) for genre in genres]


@router.get("/{genre_id}",
            response_model=GenreResponse,
            summary="Получить жанр по id")
async def genre_detail(genre_id: uuid.UUID,
                       genre_by_id: Annotated[
                           GenreByIdHandlerProtocol, Depends(genre_by_id_handler)],
                       _auth_user: Annotated[Optional[AuthUserIdentity], Depends(optional_auth_identity)]) \
        -> GenreResponse:
    query = GetGenreById(id=genre_id)
    genre = await genre_by_id.handle(query)
    return GenreResponse.from_domain(genre)
