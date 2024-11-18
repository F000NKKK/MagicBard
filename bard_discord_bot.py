import discord
import os
import asyncio
import logging
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio

class BardDiscordBot:


# Method to join the voice channel
    async def join_to_channel(self, interaction: discord.Interaction):
        try:
            if interaction.user.voice:  # Проверка, если пользователь в голосовом канале
                channel = interaction.user.voice.channel
                if not self.voice_client or not self.voice_client.is_connected():  # Проверка, если бот уже в канале
                    self.voice_client = await channel.connect()
                    self.logger.info(f"[join_to_channel] Bot joined voice channel: {channel.name}")
                    await interaction.response.send_message(f"Joined {channel.name}!")
                else:
                    await interaction.response.send_message("[join_to_channel] Already connected to a voice channel.")
            else:
                await interaction.response.send_message("[join_to_channel] You are not in a voice channel.")
        except Exception as e:
            self.logger.error(f"[join_to_channel] Error in join command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("[join_to_channel] Failed to join the voice channel.")
    
    # Method to play the next track in the playlist
    async def play_next_track(self):
        """Play the next track in the playlist."""
        if self.is_playing:  # Проверка, если трек уже воспроизводится
            self.logger.info("[play_next_track] Track already playing. Skipping next track.")
            return
    
        try:
            self.is_playing = True  # Устанавливаем флаг воспроизведения
    
            next_track = self.playlist_controller.get_track()
            if not next_track:
                self.logger.info("[play_next_track] Playlist is empty. No tracks to play.")
                self.is_playing = False
                return
    
            track_path = f"./playlist/{next_track['path']}"
            self.current_track = next_track
    
            if not os.path.exists(track_path):
                self.logger.error(f"[play_next_track] Track file not found: {track_path}")
                self.is_playing = False
                return
    
            self.logger.info(f"[play_next_track] Loading next track: {next_track['title']}")
    
            # Функция после завершения воспроизведения
            def after_playing(error):
                if error:
                    self.logger.error(f"[play_next_track] Error playing track: {error}")
                else:
                    self.logger.info(f"[play_next_track] Finished playing: {self.current_track['title']}")
            
                self.is_playing = False  # Сбрасываем флаг воспроизведения
                if not self.voice_client.is_playing():  # Если бот не воспроизводит, продолжаем с следующего трека
                    asyncio.run_coroutine_threadsafe(self.play_next_track(), self.loop)
    
            # Начинаем воспроизведение трека
            self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
            self.logger.info(f"[play_next_track] Now playing: {next_track['title']}")
    
        except Exception as e:
            self.logger.error(f"[play_next_track] Error in play_next_track: {e}")
            self.is_playing = False  # Сбрасываем флаг воспроизведения

    def __init__(self, token, config_loader, playlist_controller, downloader, logger):
        self.logger = logger
        self.token = token
        self.config_loader = config_loader
        self.playlist_controller = playlist_controller
        self.downloader = downloader
        self.voice_client = None
        self.current_track = None
        self.is_playing = False  # Флаг для проверки состояния воспроизведения

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            # Создаем новый event loop, если его нет
            if not asyncio.get_event_loop().is_running():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                self.loop = asyncio.get_event_loop()
            self.logger.info(f"[on_ready] Bot {self.bot.user} has successfully started!")
            try:
                # Синхронизируем команды только после запуска бота
                await self.bot.tree.sync()
                self.logger.info("[on_ready] Slash commands synchronized successfully.")
            except Exception as e:
                self.logger.error(f"[on_ready] Error syncing commands: {e}")

        # Command to join voice channel
        @self.bot.tree.command(name="join", description="Join your voice channel")
        async def join(interaction: discord.Interaction):
            await self.join_to_channel(interaction)  # Подключаем бота, если он не в канале

        # Команда для воспроизведения плейлиста
        @self.bot.tree.command(name="play", description="Start playing the playlist")
        async def play(interaction: discord.Interaction):
            try:
                await interaction.response.defer()  # Отложенный ответ для долгих операций

                if not self.voice_client or not self.voice_client.is_connected():
                    await self.join_to_channel(interaction)  # Подключаем бота, если он не в канале

                if self.voice_client.is_playing():
                    await interaction.followup.send("Already playing music.")
                else:
                    await self.play_next_track()
                    await interaction.followup.send("Playing the playlist.")

            except Exception as e:
                self.logger.error(f"[/play] Error in play command: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message("An error occurred while playing the playlist.")
                else:
                    await interaction.followup.send("An error occurred while playing the playlist.")

        # Command /skip to skip current track
        @self.bot.tree.command(name="skip", description="Skip current track")
        async def skip(interaction: discord.Interaction):
            try:
                if self.voice_client is None or not self.voice_client.is_connected():
                    if not interaction.response.is_done():
                        await interaction.response.send_message("The bot is not connected to a voice channel.", ephemeral=True)
                    else:
                        await interaction.followup.send("The bot is not connected to a voice channel.", ephemeral=True)
                    print("[/skip] Skip command failed: Bot not connected to a voice channel.")
                    return

                if not self.voice_client.is_playing():
                    if not interaction.response.is_done():
                        await interaction.response.send_message("No track is currently playing to skip.")
                    else:
                        await interaction.followup.send("No track is currently playing to skip.")
                    print("[/skip] Skip command failed: No track currently playing.")
                    return

                # Stop the current track and play the next
                print("[/skip] Skipping current track.")
                self.voice_client.stop()
                await self.play_next_track()
                if not interaction.response.is_done():
                    await interaction.response.send_message("Skipped to the next track.")
                else:
                    await interaction.followup.send("Skipped to the next track.")
            except Exception as e:
                print(f"[/skip] Error in skip command: {e}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"An error occurred while skipping: {e}")
                else:
                    await interaction.followup.send(f"An error occurred while skipping: {e}")

        # Команда /download
        @self.bot.tree.command(name="download", description="Add track to playlist")
        async def download(interaction: discord.Interaction, url: str):
            try:
                await interaction.response.send_message("Downloading track...")
                self.logger.info(f"[/download] Downloading track from URL: {url}")
                await self.downloader.download_track(url)
                self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
                await interaction.followup.send("Track downloaded successfully!")
                self.logger.info("[/download] Track downloaded successfully!")
            except Exception as e:
                self.logger.error(f"[/download] Error in download command: {e}")
                await interaction.followup.send(f"Failed to download track: {e}")

        # Команда /stop
        @self.bot.tree.command(name="stop", description="Stop the music")
        async def stop(interaction: discord.Interaction):
            try:
                if self.voice_client and self.voice_client.is_connected():
                    await self.voice_client.disconnect()
                    self.logger.info("[/stop] Bot stopped playing and disconnected.")
                    await interaction.response.send_message("Music playback stopped.")
                else:
                    await interaction.response.send_message("Bot is not playing any music.")
            except Exception as e:
                self.logger.error(f"[/stop] Error in stop command: {e}")
                await interaction.response.send_message("Failed to stop the music.")

        # Команда /pause
        @self.bot.tree.command(name="pause", description="Pause the track playback")
        async def pause(interaction: discord.Interaction):
            try:
                if self.voice_client and self.voice_client.is_playing():
                    self.voice_client.pause()
                    self.logger.info("[/pause] Playback paused.")
                    await interaction.response.send_message("Playback paused.")
                else:
                    await interaction.response.send_message("Cannot pause, as no music is playing.")
            except Exception as e:
                self.logger.error(f"[/pause] Error in pause command: {e}")
                await interaction.response.send_message("Failed to pause playback.")

        # Команда /resume
        @self.bot.tree.command(name="resume", description="Resume the track playback")
        async def resume(interaction: discord.Interaction):
            try:
                if self.voice_client and self.voice_client.is_paused():
                    self.voice_client.resume()
                    self.logger.info("[/resume] Playback resumed.")
                    await interaction.response.send_message("Playback resumed.")
                else:
                    await interaction.response.send_message("Music is not paused.")
            except Exception as e:
                self.logger.error(f"[/resume] Error in resume command: {e}")
                await interaction.response.send_message("Failed to resume playback.")
        
        # Command /shuffle to toggle shuffle mode
        @self.bot.tree.command(name="shuffle", description="Shuffle the playlist")
        async def shuffle(interaction: discord.Interaction, mode: str):
            if mode == "t":
                self.playlist_controller.enable_shuffle()
                await interaction.response.send_message(f"Shuffle mode is now {mode}.")
            elif mode == "f":
                self.playlist_controller.disable_shuffle()
                await interaction.response.send_message(f"Shuffle mode is now {mode}.")
            else:
                await interaction.response.send_message("Invalid mode. Please use 't' or 'f'.")

        # Команда /repeat для выбора режима повтора
        @self.bot.tree.command(name="repeat", description="Выбрать режим повтора 0 - без, 1 - один трек, 2 - все треки")
        async def repeat(interaction: discord.Interaction, mode: int):
            # Проверяем, что mode является целым числом
            if not isinstance(mode, int):
                await interaction.response.send_message("Режим повтора должен быть целым числом.")
                return

            # Проверяем, что mode находится в допустимом диапазоне [0, 1, 2]
            if mode not in [0, 1, 2]:
                await interaction.response.send_message("Неверный режим повтора. Используйте 0, 1 или 2.")
                return

            # Устанавливаем режим повтора в плейлисте
            self.playlist_controller.set_repeat(mode)
            await interaction.response.send_message(f"Режим повтора установлен на {mode}.")
            
    def run(self):
        try:
            self.bot.run(self.token)
        except Exception as e:
            self.logger.critical(f"[run] Critical error: {e}")
