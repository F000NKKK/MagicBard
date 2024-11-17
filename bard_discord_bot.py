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
            try:
                # Проверка наличия объекта бота
                if not self.bot or not isinstance(self.bot, discord.Client):
                    raise ValueError("Объект бота недействителен или не найден.")

                print(f"Бот {self.bot.user} успешно запущен!")

                # Синхронизация команд при запуске
                await self.bot.tree.sync()
                print("Slash-команды успешно синхронизированы.")
            except discord.HTTPException as http_ex:
                print(f"Ошибка при синхронизации с Discord API: {http_ex}")
            except Exception as e:
                print(f"Ошибка синхронизации команд: {e}")


        async def join_channel(interaction: discord.Interaction):
            try:
                # Проверка объекта взаимодействия
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Объект взаимодействия недействителен или не найден.")

                # Проверка, находится ли пользователь в голосовом канале
                if interaction.user.voice and interaction.user.voice.channel:
                    channel = interaction.user.voice.channel

                    # Проверка, уже ли бот подключён
                    if self.voice_client and self.voice_client.is_connected():
                        await interaction.response.send_message(
                            f"Бот уже подключён к голосовому каналу: {self.voice_client.channel.name}.",
                            ephemeral=True
                        )
                        return

                    # Подключение к голосовому каналу
                    self.voice_client = await channel.connect()
                    await interaction.response.send_message(f"Бот присоединился к голосовому каналу {channel.name}.")
                else:
                    await interaction.response.send_message(
                        "Вы должны находиться в голосовом канале, чтобы использовать эту команду.",
                        ephemeral=True
                    )

            except discord.ClientException as client_ex:
                print(f"Ошибка подключения к голосовому каналу: {client_ex}")
                await interaction.response.send_message(
                    f"Ошибка подключения к голосовому каналу: {client_ex}",
                    ephemeral=True
                )
            except discord.HTTPException as http_ex:
                print(f"Ошибка взаимодействия с Discord API: {http_ex}")
                await interaction.response.send_message(
                    f"Ошибка взаимодействия с Discord API: {http_ex}",
                    ephemeral=True
                )
            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(
                    f"Ошибка валидации: {ve}",
                    ephemeral=True
                )
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                await interaction.response.send_message(
                    f"Произошла ошибка: {e}",
                    ephemeral=True
                )

                
        
        # Команда /download для скачивания трека
        @self.bot.tree.command(name="download", description="Добавить трек в плейлист")
        async def download(interaction: discord.Interaction, url: str):
            try:
                # Проверка URL
                if not url or not isinstance(url, str):
                    raise ValueError("URL трека не предоставлен или имеет неверный формат.")

                # Валидация формата URL (например, проверка на YouTube URL)
                if not (url.startswith("http://") or url.startswith("https://")):
                    raise ValueError("Указан некорректный URL. Убедитесь, что он начинается с http:// или https://.")

                # Проверка наличия строки взаимодействия
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Некорректный объект взаимодействия.")

                # Ответ перед началом загрузки
                if not interaction.response.is_done():
                    await interaction.response.send_message("Загрузка трека...")
                else:
                    await interaction.followup.send("Загрузка трека...")

                print("Загрузка трека началась...")
        
                # Асинхронная загрузка трека
                await self.downloader.download_track(url)

                # Проверка на наличие плейлиста перед сохранением
                playlist_files = self.playlist_controller.get_playlist_files()
                if not playlist_files:
                    raise ValueError("Ошибка: плейлист отсутствует или пуст.")

                # Сохранение плейлиста
                self.playlist_controller.save_playlist(playlist_files)

                # Уведомление об успешной загрузке
                if not interaction.response.is_done():
                    await interaction.response.send_message("Трек успешно загружен!")
                else:
                    await interaction.followup.send("Трек успешно загружен!")
        
                print("Трек успешно загружен!")
    
            except ValueError as ve:
                print(f"Ошибка валидации: {str(ve)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Ошибка валидации: {str(ve)}")
                else:
                    await interaction.followup.send(f"Ошибка валидации: {str(ve)}")

            except discord.HTTPException as http_ex:
                print(f"Ошибка взаимодействия с Discord API: {str(http_ex)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Ошибка взаимодействия с Discord API: {str(http_ex)}")
                else:
                    await interaction.followup.send(f"Ошибка взаимодействия с Discord API: {str(http_ex)}")
    
            except Exception as e:
                print(f"Произошла ошибка при добавлении трека: {str(e)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Произошла ошибка при добавлении трека: {str(e)}")
                else:
                    await interaction.followup.send(f"Произошла ошибка при добавлении трека: {str(e)}")


        
        # Команда /join для присоединения к голосовому каналу
        @self.bot.tree.command(name="join", description="Присоединить бота к вашему голосовому каналу")
        async def join(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта взаимодействия
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")

                # Присоединение к голосовому каналу
                await join_channel(interaction)
            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /join: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /play для включения воспроизведения
        @self.bot.tree.command(name="play", description="Включить воспроизведение плейлиста")
        async def play(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта взаимодействия
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")

                # Сохраняем и получаем файлы плейлиста
                self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
        
                # Проверяем, что voice_client присоединился к голосовому каналу
                if self.voice_client is None:
                    await join_channel(interaction)

                await asyncio.sleep(2)  # Подождать 2 секунды для подключения

                if self.voice_client is None:
                    if not interaction.response.is_done():
                        await interaction.response.send_message("Не удалось присоединиться к голосовому каналу.")
                    return
        
                # Проверяем, подключён ли бот
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
            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /play: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /stop для остановки музыки
        @self.bot.tree.command(name="stop", description="Остановить музыку")
        async def stop(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта взаимодействия
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")

                # Проверка наличия активного voice_client
                if self.voice_client is not None:
                    # Если бот подключен, отключаем его
                    await self.voice_client.disconnect()
                    if not interaction.response.is_done():
                        await interaction.response.send_message("Остановлено воспроизведение музыки.")
                    print("Остановлено воспроизведение музыки.")
                else:
                    # Если бот не воспроизводит музыку
                    if not interaction.response.is_done():
                        await interaction.response.send_message("Бот не воспроизводит музыку.")
                    print("Бот не воспроизводит музыку.")
            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /stop: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /skip для пропуска текущего трека
        @self.bot.tree.command(name="skip", description="Пропустить текущий трек")
        async def skip(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта interaction
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")

                # Проверка, что воспроизведение не началось
                if self.voice_client is None or not self.voice_client.is_playing():
                    await interaction.response.send_message("Сейчас ничего не воспроизводится.")
                    return

                # Получаем текущий трек и его название
                current_track_title = self.current_track.get("title", "Неизвестный трек")

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
                        # Проверяем, что название трека соответствует текущему
                        track_title = self.current_track.get("title", "Неизвестный трек")
                        if track_title != current_track_title:
                            await interaction.response.send_message(f"Пропустил текущий трек. Теперь играет: {track_title}")
                        else:
                            await interaction.response.send_message(f"Пропустил текущий трек. Теперь играет: {track_title}")
                    else:
                        await interaction.response.send_message(f'Не найден файл {track_path}')
                else:
                    await interaction.response.send_message("Плейлист пуст.")

            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /skip: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


       # Команда /pause для паузы
        @self.bot.tree.command(name="pause", description="Пауза воспроизведения трека")
        async def pause(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта interaction
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")
        
                # Проверка на наличие голосового клиента и воспроизведение
                if self.voice_client and self.voice_client.is_playing():
                    self.voice_client.pause()
                    await interaction.response.send_message("Воспроизведение приостановлено.")
                else:
                    await interaction.response.send_message("Невозможно поставить на паузу, так как музыка не играет.")

            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /pause: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /resume для продолжения воспроизведения
        @self.bot.tree.command(name="resume", description="Продолжить воспроизведение трека")
        async def resume(interaction: discord.Interaction):
            try:
                # Проверка валидности объекта interaction
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")
        
                # Проверка на наличие голосового клиента и состояния паузы
                if self.voice_client and self.voice_client.is_paused():
                    self.voice_client.resume()
                    await interaction.response.send_message("Воспроизведение продолжено.")
                else:
                    await interaction.response.send_message("Музыка не поставлена на паузу.")

            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /resume: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /shuffle для включения/выключения перемешивания
        @self.bot.tree.command(name="shuffle", description="Перемешать плейлист")
        async def shuffle(interaction: discord.Interaction, mode: str):
            try:
                # Проверка валидности объекта interaction
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")
        
                # Проверка корректности параметра mode
                if mode == "t":
                    self.playlist_controller.enable_shuffle()
                    await interaction.response.send_message("Плейлист перемешан.")
                elif mode == "f":
                    self.playlist_controller.disable_shuffle()
                    await interaction.response.send_message("Перемешивание выключено.")
                else:
                    await interaction.response.send_message("Некорректный аргумент. Используйте 't' для включения и 'f' для выключения.")

            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /shuffle: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


        # Команда /repeat для выбора режима повтора
        @self.bot.tree.command(name="repeat", description="Выбрать режим повтора 0 - без, 1 - один трек, 2 - все треки")
        async def repeat(interaction: discord.Interaction, mode: int):
            try:
                # Проверка валидности объекта interaction
                if not interaction or not isinstance(interaction, discord.Interaction):
                    raise ValueError("Недействительный объект взаимодействия.")
        
                # Проверка корректности режима повтора
                if mode not in [0, 1, 2]:
                    await interaction.response.send_message("Неверный режим повтора. Используйте 0, 1 или 2.")
                    return
        
                self.playlist_controller.set_repeat(mode)
                await interaction.response.send_message(f"Режим повтора установлен на {mode}.")

            except ValueError as ve:
                print(f"Ошибка валидации: {ve}")
                await interaction.response.send_message(f"Ошибка: {ve}", ephemeral=True)
            except discord.HTTPException as http_ex:
                print(f"Ошибка HTTP: {http_ex}")
                await interaction.response.send_message(f"Ошибка HTTP: {http_ex}", ephemeral=True)
            except Exception as e:
                print(f"Произошла ошибка при выполнении команды /repeat: {e}")
                await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)


    def run(self):
        self.bot.run(self.token)
