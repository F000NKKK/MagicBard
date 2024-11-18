import os
import sys
import logging
from startup import Application

# Настройка логирования
log_file = "bot.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] - %(message)s"
)

logger = logging.getLogger("MagicBardLogger")

if __name__ == "__main__":
    try:
        # Устанавливаем рабочий каталог в папку, где находится файл
        program_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_path)

        logging.info("Рабочий каталог установлен в '%s'.", program_path)

        # Инициализируем и запускаем приложение
        app = Application(logger)
        app.start()

    except Exception as e:
        logging.error("Ошибка при запуске программы", exc_info=True)
        print(f"Ошибка при запуске программы. Подробности записаны в {log_file}", file=sys.stderr)
        sys.exit(1)
