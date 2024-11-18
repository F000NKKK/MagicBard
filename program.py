import os
import sys
import logging
from startup import Application

# Настройка логирования
log_file = "error.log"
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    try:
        # Устанавливаем рабочий каталог в ту же папку, где находится файл program.py
        program_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_path)

        # Инициализируем и запускаем приложение
        app = Application()
        app.start()

    except Exception as e:
        logging.error("Ошибка при запуске программы", exc_info=True)
        print(f"Ошибка при запуске программы. Подробности записаны в {log_file}", file=sys.stderr)
        sys.exit(1)
