import discord, os, asyncio
from discord.ext import commands
from discord import app_commands
from discord import FFmpegPCMAudio
import re

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
            print(f"Bot {self.bot.user} has successfully started!")
            try:
                # Synchronize commands on startup
                await self.bot.tree.sync()
                print("Slash commands synchronized successfully.")
            except Exception as e:
                print(f"Error syncing commands: {e}")

        async def join_channel(interaction: discord.Interaction):
            if interaction.user.voice and interaction.user.voice.channel:
                channel = interaction.user.voice.channel
                self.voice_client = await channel.connect()
                await interaction.response.send_message(f"Bot has joined the voice channel {channel.name}.")
            else:
                await interaction.response.send_message(
                    "You must be in a voice channel to use this command.",
                    ephemeral=True
                )

        # Command /download to download track
        @self.bot.tree.command(name="download", description="Add track to playlist")
        async def download(interaction: discord.Interaction, url: str):
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("Downloading track...")
                else:
                    await interaction.followup.send("Downloading track...")
                print(f"Downloading track from URL: {url}")
                # Using await for async function call
                await self.downloader.download_track(url)
                # Adding track to playlist
                self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
                # Response to interaction
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Track downloaded successfully!")
                else:
                     await interaction.followup.send("Track downloaded successfully!")
                print("Track downloaded successfully!")
            except Exception as e:
                print(f"Error downloading track: {str(e)}")
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"An error occurred while adding the track: {str(e)}")
                else:
                     await interaction.followup.send(f"An error occurred while adding the track: {str(e)}")

        # Command /join to join voice channel
        @self.bot.tree.command(name="join", description="Join your voice channel")
        async def join(interaction: discord.Interaction):
            await join_channel(interaction)

        # Command /play to start playing the playlist
        @self.bot.tree.command(name="play", description="Start playing the playlist")
        async def play(interaction: discord.Interaction):
            self.playlist_controller.save_playlist(self.playlist_controller.get_playlist_files())
    
            # Ensure bot is in a voice channel
            if self.voice_client is None:
                await join_channel(interaction)

            await asyncio.sleep(2)

            # If bot failed to join voice channel
            if self.voice_client is None:
                if not interaction.response.is_done():
                    await interaction.response.send_message("Failed to join the voice channel.")
                return

            # If bot is not connected
            if not self.voice_client.is_connected():
                if not interaction.response.is_done():
                    await interaction.response.send_message("Bot is not connected to the voice channel.")
                return

            def play_next_track():
                next_track = self.playlist_controller.get_track()
                if next_track:
                    self.current_track = next_track
                    return "./playlist/" + next_track['path']
                return None

            track_path = play_next_track()
            if track_path:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"Now playing: {self.current_track['title']}")

                # Ensure bot is connected to the voice channel before playing
                if interaction.user.voice:
                    channel = interaction.user.voice.channel
                    if not self.voice_client.is_connected():
                        await channel.connect()

                # Check if the bot is already playing audio
                if self.voice_client.is_playing():
                    await interaction.response.send_message("Audio is already playing.")
                    return
        
                # Play the next track after the current one finishes
                def after_playing(error):
                    if error:
                        print(f"Error playing track: {error}")
                    else:
                        track_path = play_next_track()
                        if track_path:
                            # Ensure bot isn't already playing audio before attempting to play a new track
                            if not self.voice_client.is_playing():
                                self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                            else:
                                print("Bot is already playing audio, skipping to the next track.")
                        else:
                            asyncio.create_task(self.voice_client.disconnect())


                if os.path.exists(track_path):
                    self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                else:
                    await interaction.response.send_message(f"Track file {track_path} not found")
            else:
                await interaction.response.send_message("The playlist is empty.")


        # Command /stop to stop music
        @self.bot.tree.command(name="stop", description="Stop the music")
        async def stop(interaction: discord.Interaction):
            if self.voice_client is not None:
                await self.voice_client.disconnect()
                await interaction.response.send_message("Music playback stopped.")
            else:
                await interaction.response.send_message("Bot is not playing any music.")

        # Command /skip to skip current track
        @self.bot.tree.command(name="skip", description="Skip current track")
        async def skip(interaction: discord.Interaction):
            if self.voice_client is None or not self.voice_client.is_playing():
                await interaction.response.send_message("No track is currently playing.")
                return

            # Stop the current track
            self.voice_client.stop()

            def play_next_track():
                next_track = self.playlist_controller.get_track()
                if next_track:
                    self.current_track = next_track
                    return "./playlist/" + next_track['path']
                return None

            track_path = play_next_track()
            if track_path:
                def after_playing(error):
                    if error:
                        print(f"Error playing track: {error}")
                    else:
                        track_path = play_next_track()
                        if track_path:
                            # Ensure bot isn't already playing audio before attempting to play a new track
                            if not self.voice_client.is_playing():
                                self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                            else:
                                print("Bot is already playing audio, skipping to the next track.")
                        else:
                            asyncio.create_task(self.voice_client.disconnect())

                if os.path.exists(track_path):
                    try:
                        # Check if bot is playing before starting the next track
                        if not self.voice_client.is_playing():
                            self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
                            await interaction.response.send_message(f'Skipped current track. Now playing: {self.current_track["title"]}')
                        else:
                            print("Error: Bot is already playing audio, waiting for current track to finish.")
                    except Exception as e:
                        await interaction.response.send_message(f"Error playing track: {e}")
                else:
                    await interaction.response.send_message(f'Track file {track_path} not found')
            else:
                await interaction.response.send_message("The playlist is empty.")




        # Command /pause to pause the track
        @self.bot.tree.command(name="pause", description="Pause the track playback")
        async def pause(interaction: discord.Interaction):
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.pause()
                await interaction.response.send_message("Playback paused.")
            else:
                await interaction.response.send_message("Cannot pause, as no music is playing.")

        # Command /resume to resume playback
        @self.bot.tree.command(name="resume", description="Resume the track playback")
        async def resume(interaction: discord.Interaction):
            if self.voice_client and self.voice_client.is_paused():
                self.voice_client.resume()
                await interaction.response.send_message("Playback resumed.")
            else:
                await interaction.response.send_message("Music is not paused.")

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
        self.bot.run(self.token)
