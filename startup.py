from bard_discord_bot import BardDiscordBot
from bard_config_loader import ConfigLoader
from bard_downloader import Downloader
from bard_playlist_controller import PlaylistController

class Application:
    def __init__(self):
        self.config_loader = ConfigLoader("appsettings.json")
        self.downloader = Downloader(self.config_loader.get("yt_dlp_path", ""), self.config_loader.get("download_path", ""))
        self.playlist_controller = PlaylistController(self.config_loader.get("playlist_dir", ""))
        self.discord_bot = BardDiscordBot(
            token=self.config_loader.get("discord_token", ""),
            config_loader=self.config_loader,
            playlist_controller=self.playlist_controller,
            downloader=self.downloader
        )

    def start(self):
        self.discord_bot.run()
