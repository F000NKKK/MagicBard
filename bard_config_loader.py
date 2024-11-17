import json
import os

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            # Проверка существования файла перед попыткой открыть его
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Файл конфигурации '{self.config_file}' не найден.")

            # Проверка, что файл является допустимым JSON
            with open(self.config_file, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Ошибка при разборе JSON в файле {self.config_file}: {e}")

        except FileNotFoundError as fnf_error:
            print(f"Ошибка: {fnf_error}")
            return {}
        except ValueError as ve:
            print(f"Ошибка: {ve}")
            return {}
        except Exception as e:
            print(f"Неизвестная ошибка при загрузке конфигурации: {e}")
            return {}

    def get(self, key, default=None):
        # Проверка, что ключ является строкой
        if not isinstance(key, str):
            raise ValueError("Ключ должен быть строкой.")

        return self.config.get(key, default)
