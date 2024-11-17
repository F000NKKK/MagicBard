import discord, os, asyncio
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio

class BardDiscordBot:
    def __init__(self, token, config_loader, playlist_controller, downloader):
        self.token = token
        self.config_loader = config_loader
        self.playlist_controller = playlist_controller
        self.downloader = downloader
        self.voice_client = None
        self.current_track = None

        # Создаем объект Intents
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True  # Обязательно для Slash-команд
        intents.guilds = True
        intents.voice_states = True  # Для работы с голосовыми каналами

        # Используем commands.Bot для Slash-команд
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            print(f"Бот {self.bot.user} успешно запущен!")
            try:
                # Синхронизация команд при запуске
                await self.bot.tree.sync()
                print("Slash-команды успешно синхронизированы.")
            except Exception as e:
                print(f"Ошибка синхронизации команд: {e}")

        async def join_channel(interaction: discord.Interaction):
            if interaction.user.voice and interaction.user.voice.channel:
                channel = interaction.user.voice.channel
                self.voice_client = await channel.connect()
                await interaction.response.send_message(f"Бот присоединился к голосовому каналу {channel.name}.")
            else:
                await interaction.response.send_message(
                    "Вы должны находиться в голосовом канале, чтобы использовать эту команду.",
                    ephemeral=True
                )
                
        
        # Команда /download для скачивания трека
        @self.bot.tree.command(name="download", description="Добавить трей в плейлист")
        async def repeat(interaction: discord.Interaction, url: str):
            #await interaction.response.send_message(f"Начата загрузка трека...")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Загрузка трека...")
                else:
                    await interaction.followup.send("Загрузка трека...")
                print(f"Загрузка трека...")
                # Используем await для вызова асинхронной функции
                await self.downloader.download_track(url)
                # Добавление трека в плейлист
                self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
                # Ответ на взаимодействие
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Трек успешно загружен!")
                else:
                     await interaction.followup.send("Трек успешно загружен!")
                print(f"Трек успешно загружен!")
            except Exception as e:
                print(f"Произошла ошибка при добавлении трека: {str(e)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Произошла ошибка при добавлении трека: {str(e)}")
                else:
                     await interaction.followup.send("Произошла ошибка при добавлении трека: {str(e)}")

        
        # Команда /join для присоединения к голосовому каналу
        @self.bot.tree.command(name="join", description="Присоединить бота к вашему голосовому каналу")
        async def join(interaction: discord.Interaction):
            await join_channel(interaction)

        # Команда /play для включения воспроизведения
        @self.bot.tree.command(name="play", description="Включить воспроизведение плейлиста")
        async def play(interaction: discord.Interaction):
            self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
            
            # Проверяем, что voice_client присоединился к голосовому каналу
            if self.voice_client is None:
                await join_channel(interaction)

            await asyncio.sleep(2)  # Подождать 2 секунды для подключения

            if self.voice_client is None:
                if not interaction.response.is_done():
                    await interaction.response.send_message("Не удалось присоединиться к голосовому каналу.")
                return
            
            # Проверяем, подключен ли бот
            if not self.voice_client.is_connected():
                if not interaction.response.is_done():
                    await interaction.response.send_message("Бот не подключён к голосовому каналу.")
                return

            # Функция для воспроизведения трека
            def play_next_track():
                next_track = self.playlist_controller.get_track()
                if next_track:
                    self.current_track = next_track
                    return "./playlist/" + next_track['path']
                return None

            # Получаем путь к первому треку
            track_path = play_next_track()
            if track_path:
                # Убедитесь, что ответ будет отправлен только один раз
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Теперь играет: {self.current_track['title']}")

                # Получаем голосовой канал пользователя
                if interaction.user.voice:
                    channel = interaction.user.voice.channel
                    if not self.voice_client.is_connected():
                        await channel.connect()

                    # Воспроизводим трек
                    def after_playing(error):
                        if error:
                            print(f"Ошибка воспроизведения: {error}")
                        else:
                            # После окончания воспроизведения, продолжаем с следующим треком
                            track_path = play_next_track()
                            if track_path:
                                self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                            else:
                                # Если нет больше треков, выключаем бота
                                asyncio.create_task(self.voice_client.disconnect())

                    # Проверяем, существует ли файл
                    if os.path.exists(track_path):
                        self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                        if not interaction.response.is_done():
                            await interaction.response.send_message(f'Играю {self.current_track["title"]} в канале {channel.name}')
                    else:
                        if not interaction.response.is_done():
                            await interaction.response.send_message(f'Не найден файл {track_path}')
                else:
                    if not interaction.response.is_done():
                        await interaction.response.send_message('Ты должен быть в голосовом канале, чтобы я мог присоединиться.')
            else:
                if not interaction.response.is_done():
                    await interaction.response.send_message("Плейлист пуст.")

        # Команда /stop для остановки музыки
        @self.bot.tree.command(name="stop", description="Остановить музыку")
        async def stop(interaction: discord.Interaction):
            if self.voice_client is not None:
                await self.voice_client.disconnect()
                await interaction.response.send_message("Остановлено воспроизведение музыки.")
            else:
                await interaction.response.send_message("Бот не воспроизводит музыку.")

        # Команда /skip для пропуска текущего трека
        @self.bot.tree.command(name="skip", description="Пропустить текущий трек")
        async def skip(interaction: discord.Interaction):
            if self.voice_client is None or not self.voice_client.is_playing():
                await interaction.response.send_message("Сейчас ничего не воспроизводится.")
                return

            # Останавливаем текущий трек
            self.voice_client.stop()

            # Функция для воспроизведения следующего трека
            def play_next_track():
                next_track = self.playlist_controller.get_track()
                if next_track:
                    self.current_track = next_track
                    return "./playlist/" + next_track['path']
                return None

            # Получаем путь к следующему треку
            track_path = play_next_track()
            if track_path:
                # Воспроизведение следующего трека
                def after_playing(error):
                    if error:
                        print(f"Ошибка воспроизведения: {error}")
                    else:
                        # После окончания воспроизведения, продолжаем с следующим треком
                        track_path = play_next_track()
                        if track_path:
                            self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                        else:
                            # Если нет больше треков, выключаем бота
                            asyncio.create_task(self.voice_client.disconnect())

                # Проверяем, существует ли файл
                if os.path.exists(track_path):
                    self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                    await interaction.response.send_message(f'Пропустил текущий трек. Теперь играет: {self.current_track["title"]}')
                else:
                    await interaction.response.send_message(f'Не найден файл {track_path}')
            else:
                await interaction.response.send_message("Плейлист пуст.")

        # Команда /pause для паузы
        @self.bot.tree.command(name="pause", description="Пауза воспроизведения трека")
        async def pause(interaction: discord.Interaction):
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.pause()
                await interaction.response.send_message("Воспроизведение приостановлено.")
            else:
                await interaction.response.send_message("Невозможно поставить на паузу, так как музыка не играет.")

        # Команда /resume для продолжения воспроизведения
        @self.bot.tree.command(name="resume", description="Продолжить воспроизведение трека")
        async def resume(interaction: discord.Interaction):
            if self.voice_client and self.voice_client.is_paused():
                self.voice_client.resume()
                await interaction.response.send_message("Воспроизведение продолжено.")
            else:
                await interaction.response.send_message("Музыка не поставлена на паузу.")

        # Команда /shuffle для включения/выключения перемешивания
        @self.bot.tree.command(name="shuffle", description="Перемешать плейлист", )
        async def shuffle(interaction: discord.Interaction, mode: str):
            if mode == "t":
                self.playlist_controller.enable_shuffle()
                await interaction.response.send_message("Плейлист перемешан.")
            elif mode == "f":
                self.playlist_controller.enable_shuffle()
                await interaction.response.send_message("Перемешивание выключено.")
            else:
                await interaction.response.send_message("Некорректный аргумент")

        # Команда /repeat для выбора режима повтора
        @self.bot.tree.command(name="repeat", description="Выбрать режим повтора 0 - без, 1 - один трек, 2 - все треки")
        async def repeat(interaction: discord.Interaction, mode: int):
            if mode not in [0, 1, 2]:
                await interaction.response.send_message("Неверный режим повтора. Используйте 0, 1 или 2.")
                return
            self.playlist_controller.set_repeat(mode)
            await interaction.response.send_message(f"Режим повтора установлен на {mode}.")

    def run(self):
        self.bot.run(self.token)
