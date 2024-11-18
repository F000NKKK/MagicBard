import json
import os
import logging

class ConfigLoader:
    def __init__(self, config_file, logger):
        self.logger = logger
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        # Проверка существования файла конфигурации
        if not os.path.exists(self.config_file):
            self.logger.error(f"Файл конфигурации '{self.config_file}' не найден.")
            return {}

        try:
            # Открытие файла с указанием кодировки utf-8
            with open(self.config_file, "r", encoding="utf-8") as file:
                # Попытка загрузить JSON
                try:
                    self.logger.info(f"Загрузка конфигурации из файла '{self.config_file}'.")
                    return json.load(file)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Ошибка при парсинге JSON в файле '{self.config_file}': {e}")
                    return {}
        except (OSError, IOError) as e:
            # Обработка ошибок при открытии файла
            self.logger.error(f"Ошибка при чтении файла конфигурации '{self.config_file}': {e}")
            return {}

    def get(self, key, default=None):
        value = self.config.get(key, default)
        self.logger.debug(f"Запрошен ключ '{key}', значение: {value}")
        return value

# Пример использования
# config_loader = ConfigLoader('config.json')
# db_host = config_loader.get('db_host', 'localhost')
# self.logger.info(f"DB Host: {db_host}")
