from bard_discord_bot import BardDiscordBot
from bard_config_loader import ConfigLoader
from bard_downloader import Downloader
from bard_playlist_controller import PlaylistController
import os

class Application:
    def __init__(self):
<<<<<<< HEAD
        # Загрузка конфигурации
        self.config_loader = ConfigLoader("appsettings.json")
        
        # Валидация обязательных параметров конфигурации
        yt_dlp_path = self.config_loader.get("yt_dlp_path", "")
        download_path = self.config_loader.get("download_path", "")
        discord_token = self.config_loader.get("discord_token", "")
        playlist_dir = self.config_loader.get("playlist_dir", "")
        
        if not yt_dlp_path:
            print("Ошибка: путь к yt-dlp не указан в конфигурации.")
            return
        
        if not download_path:
            print("Ошибка: путь для скачивания не указан в конфигурации.")
            return
        
        if not discord_token:
            print("Ошибка: токен для Discord не указан в конфигурации.")
            return
        
        if not playlist_dir:
            print("Ошибка: директория для плейлистов не указана в конфигурации.")
            return
        
        # Валидация путей
        if not os.path.exists(yt_dlp_path):
            print(f"Ошибка: путь к yt-dlp '{yt_dlp_path}' не существует.")
            return
        
        if not os.path.isdir(download_path):
            print(f"Ошибка: директория для скачивания '{download_path}' не существует.")
            return
        
        if not os.path.isdir(playlist_dir):
            print(f"Ошибка: директория плейлистов '{playlist_dir}' не существует.")
            return

        # Инициализация компонентов приложения
        self.downloader = Downloader(yt_dlp_path, download_path)
        self.playlist_controller = PlaylistController(playlist_dir)
=======
        # �������� ������������ � ���������
        self.config_loader = ConfigLoader("appsettings.json")
        
        # �������� ����� ��� yt_dlp � ���������� ��������
        yt_dlp_path = self.config_loader.get("yt_dlp_path", "")
        download_path = self.config_loader.get("download_path", "")
        
        if not yt_dlp_path or not os.path.exists(yt_dlp_path):
            raise ValueError(f"������������ ���� � yt-dlp: {yt_dlp_path}")
        
        if not download_path or not os.path.isdir(download_path):
            raise ValueError(f"������������ ���� ��� ��������: {download_path}")
        
        self.downloader = Downloader(yt_dlp_path, download_path)
        
        # �������� ���� � ���������� ���������
        playlist_dir = self.config_loader.get("playlist_dir", "")
        if not playlist_dir or not os.path.isdir(playlist_dir):
            raise ValueError(f"������������ ���� � ���������� ���������: {playlist_dir}")
        
        self.playlist_controller = PlaylistController(playlist_dir)
        
        # ��������� � ��������� ������ Discord
        discord_token = self.config_loader.get("discord_token", "")
        if not discord_token:
            raise ValueError("����� Discord �� ������ ��� �����������.")
        
        # ������������� Discord ����
>>>>>>> e011704d756d619585810eb50b024b454f47513a
        self.discord_bot = BardDiscordBot(
            token=discord_token,
            config_loader=self.config_loader,
            playlist_controller=self.playlist_controller,
            downloader=self.downloader
        )

    def start(self):
        # Проверка успешной инициализации перед запуском бота
        if hasattr(self, 'discord_bot'):
            self.discord_bot.run()
        else:
            print("Не удалось инициализировать приложение. Проверьте конфигурацию.")
