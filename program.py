import os
import sys
from startup import Application

if __name__ == "__main__":
    try:
        # Устанавливаем рабочий каталог в ту же папку, где находится файл program.py
        program_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_path)

        # Инициализируем и запускаем приложение
        app = Application()
        app.start()

    except Exception as e:
        print(f"Ошибка при запуске программы: {e}", file=sys.stderr)
        sys.exit(1)
