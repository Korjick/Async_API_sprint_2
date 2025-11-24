from functools import lru_cache
from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from internal.infrastructure.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    """Настройки"""
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')
    # Название проекта. Используется в Swagger-документации
    project_name: str = Field('movies', validation_alias='PROJECT_NAME')

    # Настройки Redis
    redis_host: str = Field('127.0.0.1', validation_alias='REDIS_HOST')
    redis_port: int = Field(6379, validation_alias='REDIS_PORT')

    # Настройки Elasticsearch
    elastic_host: str = Field('127.0.0.1', validation_alias='ELASTIC_HOST')
    elastic_port: int = Field(9200, validation_alias='ELASTIC_PORT')
    elastic_schema: str = Field('https://', validation_alias='ELASTIC_SCHEMA')
