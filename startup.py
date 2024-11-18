import os
import sys
import logging
from bard_discord_bot import BardDiscordBot
from bard_config_loader import ConfigLoader
from bard_downloader import Downloader
from bard_playlist_controller import PlaylistController

class Application:
    def __init__(self, logger):
        self.logger = logger

        try:
            self.logger.info("Инициализация приложения началась.")

            # Загрузка конфигурации
            self.config_loader = ConfigLoader("appsettings.json", self.logger)
            self.logger.info("Конфигурация загружена успешно.")

            # Валидация обязательных параметров конфигурации
            self.validate_configuration()

            # Инициализация компонентов
            self.initialize_components()

            self.logger.info("Приложение успешно инициализировано.")
        except Exception as e:
            self.logger.error("Ошибка при инициализации приложения", exc_info=True)
            raise

    def validate_configuration(self):
        self.logger.info("Валидация конфигурации началась.")

        yt_dlp_path = self.config_loader.get("yt_dlp_path", "")
        download_path = self.config_loader.get("download_path", "")
        discord_token = self.config_loader.get("discord_token", "")
        playlist_dir = self.config_loader.get("playlist_dir", "")

        if not yt_dlp_path:
            raise ValueError("Путь к yt-dlp не указан в конфигурации.")
        if not download_path:
            raise ValueError("Путь для скачивания не указан в конфигурации.")
        if not discord_token:
            raise ValueError("Токен Discord не указан в конфигурации.")
        if not playlist_dir:
            raise ValueError("Директория для плейлистов не указана в конфигурации.")

        if not os.path.exists(yt_dlp_path):
            raise FileNotFoundError(f"Путь к yt-dlp '{yt_dlp_path}' не существует.")
        if not os.path.isdir(download_path):
            raise NotADirectoryError(f"Директория для скачивания '{download_path}' не существует.")
        if not os.path.isdir(playlist_dir):
            raise NotADirectoryError(f"Директория для плейлистов '{playlist_dir}' не существует.")

        self.logger.info("Валидация конфигурации завершена успешно.")

    def initialize_components(self):
        self.logger.info("Инициализация компонентов приложения.")

        yt_dlp_path = self.config_loader.get("yt_dlp_path")
        download_path = self.config_loader.get("download_path")
        playlist_dir = self.config_loader.get("playlist_dir")
        discord_token = self.config_loader.get("discord_token")

        self.downloader = Downloader(yt_dlp_path, download_path, self.logger)
        self.playlist_controller = PlaylistController(playlist_dir, "appsettings.playlistController.json", "playlist.json", self.logger)
        self.discord_bot = BardDiscordBot(
            token=discord_token,
            config_loader=self.config_loader,
            playlist_controller=self.playlist_controller,
            downloader=self.downloader,
            logger = self.logger
        )

        self.logger.info("Компоненты приложения успешно инициализированы.")

    def start(self):
        self.logger.info("Запуск приложения.")
        try:
            if hasattr(self, 'discord_bot'):
                self.discord_bot.run()
                self.logger.info("Discord бот запущен успешно.")
            else:
                self.logger.error("Discord бот не инициализирован. Проверьте конфигурацию.")
                print("Не удалось инициализировать приложение. Проверьте конфигурацию.")
        except Exception as e:
            self.logger.error("Ошибка при запуске Discord бота", exc_info=True)
            print(f"Ошибка при запуске приложения. Подробности записаны в {log_file}", file=sys.stderr)
            sys.exit(1)
