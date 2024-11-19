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
            self.logger.info("Application initialization started.")

            # Load configuration
            self.config_loader = ConfigLoader("appsettings.json", self.logger)
            self.logger.info("Configuration successfully loaded.")

            # Validate required configuration parameters
            self.validate_configuration()

            # Initialize components
            self.initialize_components()

            self.logger.info("Application successfully initialized.")
        except Exception as e:
            self.logger.error("Error during application initialization", exc_info=True)
            raise

    def validate_configuration(self):
        self.logger.info("Configuration validation started.")

        yt_dlp_path = self.config_loader.get("yt_dlp_path", "")
        download_path = self.config_loader.get("download_path", "")
        discord_token = self.config_loader.get("discord_token", "")
        playlist_dir = self.config_loader.get("playlist_dir", "")

        if not yt_dlp_path:
            raise ValueError("The path to yt-dlp is not specified in the configuration.")
        if not download_path:
            raise ValueError("The download path is not specified in the configuration.")
        if not discord_token:
            raise ValueError("The Discord token is not specified in the configuration.")
        if not playlist_dir:
            raise ValueError("The playlist directory is not specified in the configuration.")

        if not os.path.exists(yt_dlp_path):
            raise FileNotFoundError(f"The yt-dlp path '{yt_dlp_path}' does not exist.")
        if not os.path.isdir(download_path):
            raise NotADirectoryError(f"The download directory '{download_path}' does not exist.")
        if not os.path.isdir(playlist_dir):
            raise NotADirectoryError(f"The playlist directory '{playlist_dir}' does not exist.")

        self.logger.info("Configuration validation completed successfully.")

    def initialize_components(self):
        self.logger.info("Initializing application components.")

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
            logger=self.logger
        )

        self.logger.info("Application components successfully initialized.")

    def start(self):
        self.logger.info("Starting application.")
        try:
            if hasattr(self, 'discord_bot'):
                self.discord_bot.run()
                self.logger.info("Discord bot started successfully.")
            else:
                self.logger.error("Discord bot not initialized. Check the configuration.")
                print("Failed to initialize the application. Check the configuration.")
        except Exception as e:
            self.logger.error("Error while running the Discord bot", exc_info=True)
            print(f"Error while running the application. Details are logged in {log_file}", file=sys.stderr)
            sys.exit(1)
