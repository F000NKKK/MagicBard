import os
import json
import hashlib
from datetime import datetime
import random
import logging
import threading
import time

class PlaylistController:
    def __init__(self, playlist_dir, settings_file, json_file, logger):
        self.logger = logger
        if not os.path.isdir(playlist_dir):
            logger.error(f"Директория для плейлиста '{playlist_dir}' не существует.")
            raise ValueError(f"Директория для плейлиста '{playlist_dir}' не существует.")
        self.playlist_dir = playlist_dir
        self.settings_file = settings_file
        self.json_file = json_file
        self.current_track_index = 0  # Индекс текущего трека
        self.played_tracks = set()  # Хранит ID прослушанных треков

        # Загружаем настройки и плейлист при инициализации
        self.settings = self.load_settings()
        self.playlist = self.load_playlist()

        # Запускаем фоновое обновление плейлиста
        self.update_playlist_interval = 1  # Интервал обновления в секундах
        self._start_background_playlist_update()

    def _get_track_time(self, track_path):
        if not os.path.isfile(track_path):
            self.logger.error(f"Файл '{track_path}' не существует.")
            raise ValueError(f"Файл '{track_path}' не существует.")
        return str(datetime.fromtimestamp(os.path.getmtime(track_path)))

    def _generate_unique_id(self, track_path):
        if not os.path.isfile(track_path):
            self.logger.error(f"Файл '{track_path}' не существует.")
            raise ValueError(f"Файл '{track_path}' не существует.")
        hash_object = hashlib.sha1(track_path.encode())
        return hash_object.hexdigest()[:12]

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            self.logger.warning(f"Файл настроек '{self.settings_file}' не найден. Используются значения по умолчанию.")
            return {"shuffle": False, "repeat": 1}  # Используем значения по умолчанию
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                if not isinstance(settings, dict):
                    self.logger.error("Неверный формат настроек.")
                    return {"shuffle": False, "repeat": 1}
                return settings
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке настроек: {e}")
            return {"shuffle": False, "repeat": 1}

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info("Настройки сохранены.")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении настроек: {e}")

    def load_playlist(self):
        if not os.path.exists(self.json_file):
            self.logger.warning(f"Файл плейлиста '{self.json_file}' не найден. Плейлист пуст.")
            return []
        try:
            with open(self.json_file, 'r') as f:
                playlist = json.load(f)
                if not isinstance(playlist, list):
                    self.logger.error("Неверный формат плейлиста.")
                    return []
                return playlist
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке плейлиста: {e}")
            return []

    def save_playlist(self, playlist):
        try:
            with open(self.json_file, 'w') as f:
                json.dump(playlist, f, indent=4)
            self.logger.info("Плейлист сохранен.")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении плейлиста: {e}")

    def check_and_update_playlist(self):
        """Автоматически обновляет плейлист при изменении содержимого папки"""
        self.logger.info("[check_and_update_playlist] Начало обновления плейлиста...")
        current_tracks = self.get_playlist_files()
        existing_ids = {track['id'] for track in self.playlist}
        new_tracks = [track for track in current_tracks if track['id'] not in existing_ids]
        removed_tracks = [track for track in self.playlist if track['id'] not in {track['id'] for track in current_tracks}]
    
        if new_tracks:
            self.playlist.extend(new_tracks)
            self.logger.info(f"[check_and_update_playlist] Добавлены новые треки: {len(new_tracks)}.")
     
        if removed_tracks:
            self.playlist = [track for track in self.playlist if track['id'] not in {track['id'] for track in removed_tracks}]
            self.logger.info(f"[check_and_update_playlist] Удалены треки: {len(removed_tracks)}.")
     
        self.save_playlist(self.playlist)

    def get_playlist_files(self):
        tracks = []
        try:
            for f in os.listdir(self.playlist_dir):
                if f.endswith((".mp3", ".mp4", ".webm", ".flac")):
                    track_path = os.path.join(self.playlist_dir, f)
                    track_id = self._generate_unique_id(track_path)
                    title = os.path.splitext(f)[0][:40]  # Отрезаем название файла до 40 символов
                    time = self._get_track_time(track_path)
                    tracks.append({
                        "id": track_id,
                        "title": title,
                        "time": time,
                        "path": os.path.relpath(track_path, self.playlist_dir)
                    })
        except Exception as e:
            self.logger.error(f"Ошибка при получении файлов плейлиста: {e}")
        return tracks

    def _start_background_playlist_update(self):
        """Запускает фоновую задачу для обновления плейлиста каждую секунду."""
        def update_task():
            while True:
                time.sleep(self.update_playlist_interval)
                self.check_and_update_playlist()

        update_thread = threading.Thread(target=update_task, daemon=True)
        update_thread.start()

    def get_track(self):
        if len(self.playlist) == 0:
            self.logger.warning("[get_track] Плейлист пуст.")
            return None

        # Если перемешивание включено
        if self.settings["shuffle"]:
            not_played_tracks = [track for track in self.playlist if track['id'] not in self.played_tracks]
            if not_played_tracks:
                random.shuffle(not_played_tracks)
                self.playlist = not_played_tracks + [track for track in self.playlist if track['id'] in self.played_tracks]
        
            track = self.playlist[self.current_track_index]
        else:
            track = self.playlist[self.current_track_index]
        
            while track['id'] in self.played_tracks:
                self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                track = self.playlist[self.current_track_index]

        if self.settings["repeat"] == 1:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        elif self.settings["repeat"] == 2:
            pass
        elif self.settings["repeat"] == 3:
            self.played_tracks.add(track['id'])
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)

        return track

    def enable_shuffle(self):
        self.settings["shuffle"] = True
        self.save_settings()
        self.logger.info("Перемешивание включено.")

    def disable_shuffle(self):
        self.settings["shuffle"] = False
        self.save_settings()
        self.logger.info("Перемешивание отключено.")

    def set_repeat(self, mode):
        self.settings["repeat"] = mode
        self.save_settings()
        self.logger.info(f"Режим повтора установлен: {mode}")

    def clear_played_tracks(self):
        """Очистить список прослушанных треков"""
        self.played_tracks.clear()
        self.logger.info("Список прослушанных треков сброшен.")

    def remove_played_track(self):
        """Удалить прослушанный трек из плейлиста"""
        if self.playlist:
            track = self.playlist[self.current_track_index]
            self.playlist = [t for t in self.playlist if t['id'] != track['id']]
            self.logger.info(f"Трек {track['title']} удален из плейлиста.")
            self.save_playlist(self.playlist)

# Пример использования:
# playlist_controller = PlaylistController("./playlist")
# playlist_controller.save_playlist(playlist_controller.get_playlist_files())
# playlist_controller.enable_shuffle()
# playlist_controller.set_repeat(2)
# next_track = playlist_controller.get_track()
# if next_track:
#     print(f"Теперь играет: {next_track['title']}")
# playlist_controller.add_to_playlist("path/to/track.mp3")
# playlist_controller.remove_from_playlist(track_id="f4f1c8ee70e8")
