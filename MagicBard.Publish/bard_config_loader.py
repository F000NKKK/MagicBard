import json
import os
import logging

class ConfigLoader:
    def __init__(self, config_file, logger):
        self.logger = logger
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        # Check if the configuration file exists
        if not os.path.exists(self.config_file):
            self.logger.error(f"Configuration file '{self.config_file}' not found.")
            return {}

        try:
            # Open the file with UTF-8 encoding
            with open(self.config_file, "r", encoding="utf-8") as file:
                # Attempt to load JSON
                try:
                    self.logger.info(f"Loading configuration from file '{self.config_file}'.")
                    return json.load(file)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing JSON in file '{self.config_file}': {e}")
                    return {}
        except (OSError, IOError) as e:
            # Handle errors when opening the file
            self.logger.error(f"Error reading configuration file '{self.config_file}': {e}")
            return {}

    def get(self, key, default=None):
        value = self.config.get(key, default)
        self.logger.debug(f"Requested key '{key}', value: {value}")
        return value

# Example usage
# config_loader = ConfigLoader('config.json', logger)
# db_host = config_loader.get('db_host', 'localhost')
# logger.info(f"DB Host: {db_host}")

