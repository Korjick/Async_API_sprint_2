import logging
import sys
from typing import Any, Self

import structlog

from content_api.internal.ports.output.logger import Logger


class StructlogLogger(Logger):
    def __init__(self, logger: Any):
        self._logger = logger

    def branch(self, **fields: Any) -> Self:
        return self.__class__(logger=self._logger.bind(**fields))

    def bind_context(self, **fields: Any) -> None:
        structlog.contextvars.bind_contextvars(**fields)

    def clear_context(self) -> None:
        structlog.contextvars.clear_contextvars()

    def debug(self, event: str, **fields: Any) -> None:
        self._logger.debug(event, **fields)

    def info(self, event: str, **fields: Any) -> None:
        self._logger.info(event, **fields)

    def warning(self, event: str, **fields: Any) -> None:
        self._logger.warning(event, **fields)

    def error(self, event: str, **fields: Any) -> None:
        self._logger.error(event, **fields)

    def exception(self, event: str, **fields: Any) -> None:
        self._logger.exception(event, **fields)

    @classmethod
    def from_name(cls, name: str) -> Self:
        return cls(logger=structlog.get_logger(name))

    @classmethod
    def configure(cls, json_logs: bool = True, log_level: str = "INFO") -> None:
        timestamper = structlog.processors.TimeStamper(fmt="iso")
        shared_processors: list[structlog.types.Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestamper,
        ]

        if json_logs:
            renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
        else:
            renderer = structlog.dev.ConsoleRenderer(colors=True)

        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                *shared_processors,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=[
                *shared_processors,
                structlog.stdlib.ExtraAdder(),
            ],
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.format_exc_info,
                renderer,
            ],
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level.upper())
