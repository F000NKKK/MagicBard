import json
import os

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        # Проверка существования файла конфигурации
        if not os.path.exists(self.config_file):
            print(f"Ошибка: файл конфигурации '{self.config_file}' не найден.")
            return {}

        try:
            # Открытие файла с указанием кодировки utf-8
            with open(self.config_file, "r", encoding="utf-8") as file:
                # Попытка загрузить JSON
                try:
                    return json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Ошибка при парсинге JSON: {e}")
                    return {}
        except (OSError, IOError) as e:
            # Обработка ошибок при открытии файла
            print(f"Ошибка при чтении файла конфигурации: {e}")
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

# Пример использования
# config_loader = ConfigLoader('config.json')
# db_host = config_loader.get('db_host', 'localhost')
# print(f"DB Host: {db_host}")
