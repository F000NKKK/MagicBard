import os
import sys
import logging
from startup import Application

# Configure logging
log_file = "bot.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] - %(message)s"
)

logger = logging.getLogger("MagicBardLogger")

if __name__ == "__main__":
    try:
        # Set the working directory to the folder containing the script
        program_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_path)

        logging.info("Working directory set to '%s'.", program_path)

        # Initialize and start the application
        app = Application(logger)
        app.start()

    except Exception as e:
        logging.error("Error during program startup", exc_info=True)
        print(f"Error during program startup. Details are logged in {log_file}", file=sys.stderr)
        sys.exit(1)
