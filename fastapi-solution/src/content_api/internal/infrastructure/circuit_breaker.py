import asyncio
import collections
import functools
import typing

STATE_COUNT_UPPER_LIMIT = 10
ERROR_COUNT_LOWER_LIMIT = 10


class NotAliveError(Exception):
    pass


def circuit_breaker(
        state_count: int,
        error_count: int,
        network_errors: typing.List[typing.Type[Exception]],
        sleep_time_sec: float,
        open_error: typing.Type[Exception] = NotAliveError,
):
    """
    Декоратор для circuit breaker.

    Важно: состояние хранится в closure декоратора и поэтому
    общее для всех экземпляров класса в рамках процесса.
    Использовать с singleton-инстансом клиента.
    """
    if (state_count <= STATE_COUNT_UPPER_LIMIT
            or error_count >= ERROR_COUNT_LOWER_LIMIT):
        raise ValueError(
            "state_count must be > 10 and error_count must be < 10"
        )

    history = collections.deque(maxlen=state_count)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_history = list(history)

            if len(current_history) >= error_count:
                recent_errors = current_history[-error_count:]
                if all(val is False for val in recent_errors):
                    raise open_error()

            if history and history[-1] is False:
                await asyncio.sleep(sleep_time_sec)

            try:
                result = await func(*args, **kwargs)
                history.append(True)
                return result
            except Exception as error:
                if any(isinstance(error, err_type) for err_type in
                       network_errors):
                    history.append(False)
                    raise open_error() from error
                raise

        return wrapper

    return decorator
