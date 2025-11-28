from functools import wraps
from typing import Optional, Type, Callable, Awaitable, Any


class CacheProtocol:
    async def get_or_set(
        self,
        func: Callable[..., Awaitable[Any]],
        args: tuple,
        kwargs: dict,
        expire_sec: int,
        prefix: Optional[str],
        response_model: Optional[Type],
        many: bool
    ) -> Any:
        """
        Выполняет логику кэширования:
        1. Генерирует ключ.
        2. Ищет в кэше. Если есть -> возвращает.
        3. Если нет -> вызывает func(*args, **kwargs), сохраняет результат и возвращает.
        """
        pass

instance: Optional[CacheProtocol] = None


def get_instance() -> CacheProtocol:
    if instance is None:
        raise RuntimeError("Cache is not initialized")
    return instance


def cache_decorator(
        expire_sec: int = 300,
        prefix: Optional[str] = None,
        response_model: Optional[Type] = None,
        many: bool = False,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service = get_instance()
            return await cache_service.get_or_set(
                func=func,
                args=args,
                kwargs=kwargs,
                expire_sec=expire_sec,
                prefix=prefix,
                response_model=response_model,
                many=many
            )

        return wrapper

    return decorator
