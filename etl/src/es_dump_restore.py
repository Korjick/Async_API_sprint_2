import backoff
import json
import os
import glob
import logging
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from pathlib import Path
from settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('restore_process.log')
    ]
)

class ESDumpRestore:
    BASE_DIR = Path(__file__).resolve().parent
    settings = Settings()
    host = f"{settings.es_hosts}:{settings.es_port}"
    backup_dir = f"{BASE_DIR}/{settings.backup_path}"
    indexes = settings.indexes.split(',')
    
    def __init__(self):
        self.connect_elasticsearch()
    
    @backoff.on_exception(
        backoff.expo,
        (ESConnectionError,),
        max_tries=5,
        max_time=300
    )
    def connect_elasticsearch(self) -> None:
        """Установление подключения к Elasticsearch"""
        try:
            self.es = Elasticsearch([self.host])
            if not self.es.ping():
                raise ESConnectionError("Не удалось подключиться к Elasticsearch")
            logging.info("Успешное подключение к Elasticsearch")
        except ESConnectionError as e:
            logging.error(f"Ошибка подключения к Elasticsearch: {e}")
            raise

    def restore_index(self, index_name: str):
        """Востановление индекса по имени"""    
        # Восстановление маппинга
        mapping_file = f"{self.backup_dir}/{index_name}_mapping.json"
        if not os.path.exists(mapping_file):
            logging.error(f"Не найден путь: {mapping_file}")
            return
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # Извлекаем маппинг и настройки для конкретного индекса
            if index_name in mapping_data:
                index_config = mapping_data[index_name]
                mappings = index_config.get('mappings', {})
                settings = index_config.get('settings', {})
            else:
                mappings = mapping_data.get('mappings', {})
                settings = mapping_data.get('settings', {})
            
            # Создаем индекс с маппингом и настройками
            if not self.es.indices.exists(index=index_name):
                body = {}
                if settings:
                    body['settings'] = settings
                if mappings:
                    body['mappings'] = mappings
                    
                self.es.indices.create(index=index_name, body=body)
                logging.info(f"Индекс {index_name} создан с маппингом и настройками")
            else:
                logging.info(f"Индекс {index_name} уже существует")
                
        except Exception as e:
            logging.error(f"Ошибка при восстановлении маппинга для {index_name}: {e}")
            return
    
        # Восстановление данных
        data_file = f"{self.backup_dir}/{index_name}_data.jsonl"
        if not os.path.exists(data_file):
            logging.error(f"Не найден путь: {data_file}")
            return
        try:
            restored_count = 0
            with open(data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        doc = json.loads(line.strip())
                        self.es.index(
                            index=index_name,
                            id=doc.get('_id'),
                            body=doc['_source']
                        )
                        restored_count += 1
            
            logging.info(f"Восстановлено документов в {index_name}: {restored_count}")
            
        except Exception as e:
            logging.error(f"Ошибка при восстановлении данных для {index_name}: {e}")

    def restore_all_indices(self):
        """Восстанавление всех индексов в директории"""
        # Находим все файлы с маппингами
        mapping_files = glob.glob(f"{self.backup_dir}/*_mapping.json")
        
        for mapping_file in mapping_files:
            index_name = os.path.basename(mapping_file).replace('_mapping.json', '')
            logging.info(f"Восстановление индекса: {index_name}")
            self.restore_index(index_name)

    def check_indexes(self):
        "Проверка созданных индексов"
        indices = list(self.es.indices.get_alias(index="*"))
        logging.info(f"Всего индексов в Elasticsearch: {len(indices)}")
        for index in self.indexes:
            if index in indices:
                count = self.es.count(index=index)['count']
                logging.info(f"{index}: {count} документов")
            else:
                logging.warning(f"Индекс {index} не был создан")
        

if __name__ == "__main__":
    restor_dump = ESDumpRestore()
    restor_dump.restore_all_indices()
    restor_dump.check_indexes()