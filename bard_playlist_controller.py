import os
import json
import hashlib
from datetime import datetime
import random

class PlaylistController:
    def __init__(self, playlist_dir, settings_file="appsettings.playlistController.json", json_file="playlist.json"):
        self.playlist_dir = playlist_dir
        self.settings_file = settings_file
        self.json_file = json_file
        self.current_track_index = 0  # Индекс текущего трека для поочередного воспроизведения

        # Загружаем настройки и плейлист при инициализации
        self.settings = self.load_settings()
        self.playlist = self.load_playlist()

    def _get_track_time(self, track_path):
        # Пример получения времени трека (по длине файла в секундах или с использованием библиотеки для аудио)
        return str(datetime.fromtimestamp(os.path.getmtime(track_path)))

    def _generate_unique_id(self, track_path):
        # Генерация 12-значного ID на основе хэша пути файла
        hash_object = hashlib.sha1(track_path.encode())  # Используем SHA-1 для генерации хэша
        return hash_object.hexdigest()[:12]  # Обрезаем хэш до 12 символов

    def load_settings(self):
        # Загружаем настройки из файла
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            else:
                return {"shuffle": False, "repeat": 1}
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            return {"shuffle": False, "repeat": 1}

    def save_settings(self):
        # Сохраняем настройки в файл
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Настройки сохранены.")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    def load_playlist(self):
        # Загружаем плейлист из файла
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Ошибка при загрузке плейлиста: {e}")
            return []

    def get_playlist_files(self):
        # Получение списка файлов для плейлиста с нужными полями
        try:
            tracks = []
            for f in os.listdir(self.playlist_dir):
                if f.endswith(".mp3") or f.endswith(".mp4") or f.endswith(".webm") or f.endswith(".flac"):
                    track_path = os.path.join(self.playlist_dir, f)
                    track_id = self._generate_unique_id(track_path)  # Генерация уникального 12-значного ID
                    title = os.path.splitext(f)[0][:40]  # Отрезаем название файла до 20 символов
                    time = self._get_track_time(track_path)
                    tracks.append({
                        "id": track_id,
                        "title": title,
                        "time": time,
                        "path": os.path.relpath(track_path, self.playlist_dir)
                    })
            return tracks
        except Exception as e:
            print(f"Ошибка при получении файлов плейлиста: {e}")
            return []

    def get_track(self):
        # Возвращает следующий трек в зависимости от настроек repeat и shuffle
        if len(self.playlist) == 0:
            print("Плейлист пуст.")
            return None

        if self.settings["shuffle"]:
            random.shuffle(self.playlist)  # Перемешиваем плейлист

        if self.settings["repeat"] == 1:  # Repeat All
            track = self.playlist[self.current_track_index]
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)  # Переходим к следующему треку
            return track
        elif self.settings["repeat"] == 2:  # Repeat One
            track = self.playlist[0]  # Повторяем первый трек
            return track
        elif self.settings["repeat"] == 3:  # No Repeat
            track = self.playlist[self.current_track_index]
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)  # Переходим к следующему треку
            return track
        else:
            return None
        playlist_controller.save_playlist(playlist_controller.get_playlist_files())
        self.playlist = self.load_playlist()  # Перезагружаем плейлист после добавления

    def add_to_playlist(self, track_path):
        try:
            if os.path.exists(track_path):
                destination = os.path.join(self.playlist_dir, os.path.basename(track_path))
                os.rename(track_path, destination)
                print(f"Трек {track_path} добавлен в плейлист.")
                playlist_controller.save_playlist(playlist_controller.get_playlist_files())
                self.playlist = self.load_playlist()  # Перезагружаем плейлист после добавления
                return True
            else:
                print(f"Трек {track_path} не найден.")
                return False
        except Exception as e:
            print(f"Ошибка при добавлении трека в плейлист: {e}")
            return False

    def remove_from_playlist(self, track_id):
        try:
            track_to_remove = None
            for track in self.playlist:
                if track['id'] == track_id:
                    track_to_remove = track
                    break
            if track_to_remove:
                track_path = os.path.join(self.playlist_dir, track_to_remove['path'])
                if os.path.exists(track_path):
                    os.remove(track_path)
                    self.playlist.remove(track_to_remove)
                    print(f"Трек с ID {track_id} удален.")
                    self.save_playlist(self.playlist)  # Сохраняем изменения в плейлисте
                    return True
                else:
                    print(f"Трек с ID {track_id} не найден на диске.")
                    return False
            else:
                print(f"Трек с ID {track_id} не найден в плейлисте.")
                return False
        except Exception as e:
            print(f"Ошибка при удалении трека: {e}")
            return False

    def save_playlist(self, tracks):
        try:
            with open(self.json_file, 'w') as f:
                json.dump(tracks, f, indent=4)
            print("Плейлист сохранен.")
        except Exception as e:
            print(f"Ошибка при сохранении плейлиста: {e}")

    def enable_shuffle(self):
        self.settings["shuffle"] = True
        self.save_settings()

    def disable_shuffle(self):
        self.settings["shuffle"] = False
        self.save_settings()

    def set_repeat(self, repeat_mode):
        if repeat_mode in [1, 2, 3]:
            self.settings["repeat"] = repeat_mode
            self.save_settings()
        else:
            print("Неверный режим repeat.")


# Пример использования
#playlist_controller = PlaylistController("./playlist")
#
# Обновляем плейлист
#playlist_controller.save_playlist(playlist_controller.get_playlist_files())
#
# Включить shuffle
#playlist_controller.enable_shuffle()
#
# Установить repeat mode на "Повторить один"
#playlist_controller.set_repeat(2)
#
# Получить следующий трек для воспроизведения
#next_track = playlist_controller.get_track()
#if next_track:
#    print(f"Теперь играет: {next_track['title']}")
#
# Добавить трек в плейлист
#playlist_controller.add_to_playlist("path/to/track.mp3")
#
# Удалить трек по ID
#playlist_controller.remove_from_playlist(track_id="f4f1c8ee70e8")
