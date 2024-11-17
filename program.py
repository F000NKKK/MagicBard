import os
from startup import Application

if __name__ == "__main__":
    # Устанавливаем рабочий каталог в ту же папку, где находится файл program.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    # Проверяем, что директория существует
    if not os.path.isdir(current_dir):
        raise ValueError(f"Не удалось найти рабочую директорию: {current_dir}")

    # Инициализируем и запускаем приложение
    try:
        app = Application()
        app.start()
    except ValueError as e:
        print(f"Ошибка инициализации приложения: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
