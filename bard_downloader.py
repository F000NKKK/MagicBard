import asyncio
import os

class Downloader:
    def __init__(self, yt_dlp_path, download_path):
        # Проверка наличия пути к yt-dlp
        if not os.path.isfile(yt_dlp_path):
            raise ValueError(f"Указанный путь к yt-dlp не существует: {yt_dlp_path}")
        self.yt_dlp_path = yt_dlp_path

        # Проверка корректности пути для скачивания
        if not os.path.isdir(download_path):
            raise ValueError(f"Указанный путь для скачивания не существует: {download_path}")
        self.download_path = download_path
        
        # Проверка существования пути для скачивания, если нет - создаем
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    async def download_track(self, url):
        if not url:
            print("Ошибка: URL не указан.")
            return None

        try:
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
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")

            # Проверка кода возврата
            if process.returncode != 0:
                raise Exception(f"Ошибка скачивания: {stderr.decode().strip()}")

            # Поиск строки с местоположением файла
            for line in stdout.decode().splitlines():
                if "[download] Destination:" in line:
                    # Возвращаем путь к файлу, если найдено
                    return line.split(": ", 1)[1].strip()

            # Если местоположение не найдено
            raise Exception("Не удалось найти местоположение файла после скачивания.")

        except Exception as e:
            print(f"Ошибка при загрузке трека: {e}")
            return None


# Пример вызова
#async def main():
#    down = Downloader('./yt-dlp.exe', './playlist')
#    file_path = await down.download_track('https://www.youtube.com/watch?v=1ll3FvVk6BA')
#    if file_path:
#        print(f"Трек успешно загружен: {file_path}")
#    else:
#        print("Не удалось загрузить трек.")
#
# Запуск асинхронного кода
#asyncio.run(main())

