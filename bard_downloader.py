import asyncio
import os
import logging

class Downloader:
    def __init__(self, yt_dlp_path, download_path, logger):
        self.logger = logger
        self.yt_dlp_path = yt_dlp_path
        self.download_path = download_path

        # Валидация пути для yt-dlp
        if not os.path.isfile(self.yt_dlp_path):
            self.logger.error(f"Файл {self.yt_dlp_path} не найден или не является исполнимым файлом.")
            raise FileNotFoundError(f"Файл {self.yt_dlp_path} не найден или не является исполнимым файлом.")

        # Проверка существования пути для скачивания и создание папки, если ее нет
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
                self.logger.info(f"Создана папка для скачивания: {self.download_path}")
            except Exception as e:
                self.logger.error(f"Не удалось создать папку для скачивания: {e}")
                raise PermissionError(f"Не удалось создать папку для скачивания: {e}")

    async def download_track(self, url):
        try:
            self.logger.info(f"Начало скачивания трека по URL: {url}")

            # Запуск команды с помощью asyncio
            process = await asyncio.create_subprocess_exec(
                self.yt_dlp_path,
                url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.download_path
            )

            # Считывание stdout и stderr
            stdout, stderr = await process.communicate()

            # Логирование для отладки
            self.logger.info(f"stdout: {stdout.decode()}")
            self.logger.error(f"stderr: {stderr.decode()}")

            # Проверка кода возврата
            if process.returncode != 0:
                error_message = f"Ошибка скачивания: {stderr.decode().strip()}"
                self.logger.error(error_message)
                raise Exception(error_message)

            # Поиск строки с местоположением файла
            for line in stdout.decode().splitlines():
                if "[download] Destination:" in line:
                    file_path = line.split(": ", 1)[1].strip()
                    self.logger.info(f"Трек успешно загружен: {file_path}")
                    return file_path

            # Если местоположение не найдено
            error_message = "Не удалось найти местоположение файла после скачивания."
            self.logger.error(error_message)
            raise Exception(error_message)

        except FileNotFoundError as e:
            self.logger.error(f"Ошибка: {e}")
            return None
        except PermissionError as e:
            self.logger.error(f"Ошибка доступа: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке трека: {e}", exc_info=True)
            return None


# Пример вызова
# async def main():
#     down = Downloader('./yt-dlp.exe', './playlist')
#     file_path = await down.download_track('https://www.youtube.com/watch?v=1ll3FvVk6BA')
#     if file_path:
#         self.logger.info(f"Трек успешно загружен: {file_path}")
#     else:
#         self.logger.error("Не удалось загрузить трек.")
#
# # Запуск асинхронного кода
# asyncio.run(main())
