from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from internal.pkg.errors import ObjectNotFoundError, ValueIsInvalidError


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ObjectNotFoundError)
    async def object_not_found_handler(request: Request, exc: ObjectNotFoundError):
        return ORJSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueIsInvalidError)
    async def value_invalid_handler(request: Request, exc: ValueIsInvalidError):
        return ORJSONResponse(status_code=400, content={"detail": str(exc)})

