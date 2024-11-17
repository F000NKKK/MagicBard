from bard_discord_bot import BardDiscordBot
from bard_config_loader import ConfigLoader
from bard_downloader import Downloader
from bard_playlist_controller import PlaylistController
import os

class Application:
    def __init__(self):
        # Загрузка конфигурации с проверкой
        self.config_loader = ConfigLoader("appsettings.json")
        
        # Проверка путей для yt_dlp и директории загрузки
        yt_dlp_path = self.config_loader.get("yt_dlp_path", "")
        download_path = self.config_loader.get("download_path", "")
        
        if not yt_dlp_path or not os.path.exists(yt_dlp_path):
            raise ValueError(f"Некорректный путь к yt-dlp: {yt_dlp_path}")
        
        if not download_path or not os.path.isdir(download_path):
            raise ValueError(f"Некорректный путь для загрузки: {download_path}")
        
        self.downloader = Downloader(yt_dlp_path, download_path)
        
        # Проверка пути к директории плейлиста
        playlist_dir = self.config_loader.get("playlist_dir", "")
        if not playlist_dir or not os.path.isdir(playlist_dir):
            raise ValueError(f"Некорректный путь к директории плейлиста: {playlist_dir}")
        
        self.playlist_controller = PlaylistController(playlist_dir)
        
        # Получение и валидация токена Discord
        discord_token = self.config_loader.get("discord_token", "")
        if not discord_token:
            raise ValueError("Токен Discord не найден или некорректен.")
        
        # Инициализация Discord бота
        self.discord_bot = BardDiscordBot(
            token=discord_token,
            config_loader=self.config_loader,
            playlist_controller=self.playlist_controller,
            downloader=self.downloader
        )

    def start(self):
        self.discord_bot.run()
