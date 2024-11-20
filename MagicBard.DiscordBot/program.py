import os
import sys
import logging
from bard_discord_bot import BardDiscordBot
from bard_config_loader import ConfigLoader

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

        discord_token = self.config_loader.get("discord_token", "")
        playlist_dir = self.config_loader.get("playlist_dir", "")

        if not discord_token:
            self.logger.error("The Discord token is not specified in the configuration.")
            raise ValueError("The Discord token is not specified in the configuration.")
        if not playlist_dir:
            self.logger.error("The playlist directory is not specified in the configuration.")
            raise ValueError("The playlist directory is not specified in the configuration.")

        if not os.path.isdir(playlist_dir):
            self.logger.error(f"The playlist directory '{playlist_dir}' does not exist.")
            raise NotADirectoryError(f"The playlist directory '{playlist_dir}' does not exist.")

        self.logger.info("Configuration validation completed successfully.")

    def initialize_components(self):
        self.logger.info("Initializing application components.")

        playlist_dir = self.config_loader.get("playlist_dir")
        discord_token = self.config_loader.get("discord_token")

        self.discord_bot = BardDiscordBot(
            token=discord_token,
            config_loader=self.config_loader,
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
        except KeyboardInterrupt:
            self.logger.info("Application terminated by user.")
            print("Application terminated by user.")
            sys.exit(0)
        except Exception as e:
            self.logger.error("Error while running the Discord bot", exc_info=True)
            print("Error while running the application. Check logs for details.", file=sys.stderr)
            sys.exit(1)


def setup_logger():
    log_file = "application.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("MagicBardBotLogger")
    return logger

if __name__ == "__main__":
    try:
        logger = setup_logger()
        # Set the working directory to the folder containing the script
        program_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_path)

        logging.info("Working directory set to '%s'.", program_path)

        # Initialize and start the application
        app = Application(logger)
        app.start()

    except Exception as e:
        logger.error("Fatal error in main application.", exc_info=True)
        print("A fatal error occurred. Check logs for details.", file=sys.stderr)
        sys.exit(1)

