import hashlib
import json
from typing import Optional, Type, Callable, Awaitable, Any

from pydantic import BaseModel
from redis.asyncio import Redis

from internal.ports.output.cache import CacheProtocol


class RedisCache(CacheProtocol):
    def __init__(self, redis_client: Redis, app_title: str):
        self.redis = redis_client
        self.app_title = app_title

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
        actual_prefix = prefix or f"{self.app_title}:{self.__class__.__name__}:{func.__name__}"
        cache_key = self._generate_cache_key(actual_prefix, *args, **kwargs)

        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return self._deserialize(cached_data, response_model, many)

        result = await func(*args, **kwargs)
        to_cache = self._serialize(result, many)
        await self.redis.set(cache_key, to_cache, ex=expire_sec)

        return result

    @staticmethod
    def _deserialize(cached_data, response_model, many):
        if isinstance(cached_data, bytes):
            cached_data = cached_data.decode("utf-8")

        raw = json.loads(cached_data)

        if response_model is None:
            return raw

        if isinstance(response_model, type) and issubclass(response_model,
                                                           BaseModel):
            if many:
                return [response_model.model_validate(item) for item in raw]
            else:
                return response_model.model_validate(raw)

        if many and isinstance(raw, list):
            return [response_model(item) for item in raw]
        return response_model(raw)

    @staticmethod
    def _serialize(result, many) -> str:
        if isinstance(result, BaseModel):
            return result.model_dump_json()
        elif many and isinstance(result, list) and result and isinstance(
                result[0], BaseModel):
            return json.dumps([item.model_dump(mode='json') for item in result])
        else:
            return json.dumps(result, default=str)

    @staticmethod
    def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
        key_parts = []
        for arg in args:
            if isinstance(arg, BaseModel):
                key_parts.append(arg.model_dump_json())
            else:
                key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            if isinstance(v, BaseModel):
                v_str = v.model_dump_json()
            else:
                v_str = str(v)
            key_parts.append(f"{k}:{v_str}")

        if not key_parts:
            return prefix

        params_str = ":".join(key_parts)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
