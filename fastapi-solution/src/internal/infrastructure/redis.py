import hashlib
import json
import logging
from functools import wraps
from typing import Optional, Type

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Генерирует уникальный ключ кэша.
    Учитывает содержимое Pydantic-моделей в аргументах для уникальности ключа.
    """
    key_parts = []

    for arg in args:
        if isinstance(arg, BaseModel):
            # model_dump_json гарантирует уникальную строку для содержимого модели
            key_parts.append(arg.model_dump_json())
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        if isinstance(v, BaseModel):
            v_str = v.model_dump_json()
        else:
            v_str = str(v)
        key_parts.append(f"{k}:{v_str}")

    # Если аргументов нет, используем только префикс
    if not key_parts:
        return prefix

    params_str = ":".join(key_parts)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()

    return f"{prefix}:{params_hash}"


def cache_response(
        expire_sec: int = 300,
        prefix: Optional[str] = None,
        response_model: Optional[Type[BaseModel]] = None,
        many: bool = False,
        redis_attr: str = "redis",
        app_title_attr: str = "app_title"
):
    """
    Декоратор для кэширования ответов методов класса.

    :param expire_sec: Время жизни кэша в секундах.
    :param prefix: Префикс ключа (по умолчанию Project:Class:Method).
    :param response_model: Pydantic-модель для валидации и десериализации ответа.
    :param many: Установить True, если метод возвращает список (List[Model]).
    :param redis_attr: Имя атрибута экземпляра класса (self), где хранится Redis клиент.
    :param app_title_attr: Имя атрибута экземпляра класса (self), где хранится имя проекта.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            redis = getattr(self, redis_attr, None)
            if not redis:
                logger.warning(
                    f"Redis client not found in {self.__class__.__name__}")
                return await func(self, *args, **kwargs)
            app_title = getattr(self, app_title_attr, None)
            if not app_title:
                logger.warning(f"App title not found in {self.__class__.__name__}")
                return await func(self, *args, **kwargs)

            actual_prefix = prefix or f"{app_title}:{self.__class__.__name__}:{func.__name__}"
            cache_key = _generate_cache_key(actual_prefix, *args, **kwargs)

            cached_data = await redis.get(cache_key)

            if cached_data:
                if response_model:
                    if many:
                        data_list = json.loads(cached_data)
                        return [response_model.model_validate(item) for item in
                                data_list]
                    else:
                        return response_model.model_validate_json(cached_data)

                return json.loads(cached_data)

            result = await func(self, *args, **kwargs)

            if result is not None:
                if many and isinstance(result, list):
                    serialized = json.dumps([
                        item.model_dump() if isinstance(item,
                                                        BaseModel) else item
                        for item in result
                    ], default=str)
                elif isinstance(result, BaseModel):
                    serialized = result.model_dump_json()
                else:
                    serialized = json.dumps(result, default=str)

                await redis.set(cache_key, serialized, expire_sec)

            return result

        return wrapper

    return decorator
