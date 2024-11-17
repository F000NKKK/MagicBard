import os
from startup import Application

if __name__ == "__main__":
    # Устанавливаем рабочий каталог в ту же папку, где находится файл program.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Инициализируем и запускаем приложение
    app = Application()
    app.start()
