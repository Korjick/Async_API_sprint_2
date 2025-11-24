from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки"""
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')

    es_hosts: str = Field(default='http://127.0.0.1',
                          validation_alias='ELASTIC_HOST')
    es_port: int = Field(default=9200, validation_alias='ELASTIC_PORT')
    backup_path: str = Field(default='backup', validation_alias='BACKUP_PATH')
    indexes: str = Field(default='movies,genres,persons',
                         validation_alias='INDEXES')
