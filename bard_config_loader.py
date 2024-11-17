import json

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)
