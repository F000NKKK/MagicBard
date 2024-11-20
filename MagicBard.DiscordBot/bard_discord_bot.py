import discord
import os
import asyncio
import requests
import logging
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio

class BardDiscordBot:
    # Method to join the voice channel
    async def join_to_channel(self, interaction: discord.Interaction):
        try:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                if not self.voice_client or not self.voice_client.is_connected():
                    self.voice_client = await channel.connect()
                    self.logger.info(f"[join_to_channel] Bot joined voice channel: {channel.name}")
                    await interaction.followup.send(f"Joined {channel.name}!")
                else:
                    await interaction.followup.send("Already connected to a voice channel.")
            else:
                await interaction.followup.send("You are not in a voice channel.")
        except Exception as e:
            self.logger.error(f"[join_to_channel] Error in join command: {e}")
            await interaction.followup.send("Failed to join the voice channel.")

    # Method to play the next track in the playlist
    async def play_next_track(self):
        """Play the next track in the playlist."""
        if self.is_playing:
            self.logger.info("[play_next_track] Track already playing. Skipping next track.")
            return

        try:
            self.is_playing = True

            response = requests.get("http://127.0.0.1:58912/api/Playlist/next")
            if response.status_code != 200:
                self.logger.error(f"[play_next_track] Failed to fetch next track. HTTP {response.status_code}: {response.text}")
                self.is_playing = False
                return

            next_track = response.json()

            # Check if the next track response is invalid or empty (playlist has ended)
            if not next_track or not next_track.get('title') or not next_track.get('path'):
                self.logger.info("[play_next_track] Playlist is empty or reached the end. No tracks to play.")
                self.is_playing = False
                return

            track_path = f"./playlist/{next_track['path']}"
            self.current_track = next_track

            if not os.path.exists(track_path):
                self.logger.error(f"[play_next_track] Track file not found: {track_path}")
                self.is_playing = False
                return

            self.logger.info(f"[play_next_track] Loading next track: {next_track['title']}")

            def after_playing(error):
                if error:
                    self.logger.error(f"[play_next_track] Error playing track: {error}")
                else:
                    self.logger.info(f"[play_next_track] Finished playing: {self.current_track['title']}")

                self.is_playing = False
                if not self.voice_client.is_playing():
                    asyncio.run_coroutine_threadsafe(self.play_next_track(), self.loop)

            self.voice_client.play(FFmpegPCMAudio(track_path), after=after_playing)
            self.logger.info(f"[play_next_track] Now playing: {next_track['title']}")

        except requests.RequestException as e:
            self.logger.error(f"[play_next_track] HTTP request error: {e}")
            self.is_playing = False
        except Exception as e:
            self.logger.error(f"[play_next_track] Unexpected error: {e}")
            self.is_playing = False

    def __init__(self, token, config_loader, logger):
        self.logger = logger
        self.token = token
        self.config_loader = config_loader
        self.voice_client = None
        self.current_track = None
        self.is_playing = False

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            if not asyncio.get_event_loop().is_running():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                self.loop = asyncio.get_event_loop()
            self.logger.info(f"[on_ready] Bot {self.bot.user} has successfully started!")
            try:
                await self.bot.tree.sync()
                self.logger.info("[on_ready] Slash commands synchronized successfully.")
            except Exception as e:
                self.logger.error(f"[on_ready] Error syncing commands: {e}")

        # Command to join voice channel
        @self.bot.tree.command(name="join", description="Join your voice channel")
        async def join(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()
            await self.join_to_channel(interaction)

        # Command to start playing the playlist
        @self.bot.tree.command(name="play", description="Start playing the playlist")
        async def play(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()
            
            try:
                # If the bot is not connected to a voice channel, make it join
                if not self.voice_client or not self.voice_client.is_connected():
                    await self.join_to_channel(interaction)

                # If the bot is already playing music, send a message
                if self.voice_client.is_playing():
                    await interaction.followup.send("Already playing music.")
                else:
                    await self.play_next_track()
                    await interaction.followup.send("Playing the playlist.")

            except Exception as e:
                # Log error and send message
                self.logger.error(f"[/play] Error in play command: {e}")
                await interaction.followup.send("An error occurred while playing the playlist.")


        @self.bot.tree.command(name="skip", description="Skip current track")
        async def skip(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()

            try:
                if self.voice_client is None or not self.voice_client.is_connected():
                    await interaction.followup.send("The bot is not connected to a voice channel.", ephemeral=True)
                    print("[/skip] Skip command failed: Bot not connected to a voice channel.")
                    return

                if not self.voice_client.is_playing():
                    await interaction.followup.send("No track is currently playing to skip.")
                    print("[/skip] Skip command failed: No track currently playing.")
                    return

                print("[/skip] Skipping current track.")
                self.voice_client.stop()
                await self.play_next_track()

                await interaction.followup.send("Skipped to the next track.")
            except Exception as e:
                print(f"[/skip] Error in skip command: {e}")
                await interaction.followup.send(f"An error occurred while skipping: {e}")

        @self.bot.tree.command(name="stop", description="Stop the music")
        async def stop(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()

            try:
                if self.voice_client and self.voice_client.is_connected():
                    await self.voice_client.disconnect()
                    self.logger.info("[/stop] Bot stopped playing and disconnected.")
                    await interaction.followup.send("Music playback stopped.")
                else:
                    await interaction.followup.send("Bot is not playing any music.")
            except Exception as e:
                self.logger.error(f"[/stop] Error in stop command: {e}")
                await interaction.followup.send("Failed to stop the music.")


        @self.bot.tree.command(name="pause", description="Pause the track playback")
        async def pause(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()

            try:
                if self.voice_client and self.voice_client.is_playing():
                    self.voice_client.pause()
                    self.logger.info("[/pause] Playback paused.")
                    await interaction.followup.send("Playback paused.")
                else:
                    await interaction.followup.send("Cannot pause, as no music is playing.")
            except Exception as e:
                self.logger.error(f"[/pause] Error in pause command: {e}")
                await interaction.followup.send("Failed to pause playback.")


        @self.bot.tree.command(name="resume", description="Resume the track playback")
        async def resume(interaction: discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()

            try:
                if self.voice_client and self.voice_client.is_paused():
                    self.voice_client.resume()
                    self.logger.info("[/resume] Playback resumed.")
                    await interaction.followup.send("Playback resumed.")
                else:
                    await interaction.followup.send("Music is not paused.")
            except Exception as e:
                self.logger.error(f"[/resume] Error in resume command: {e}")
                await interaction.followup.send("Failed to resume playback.")


        @self.bot.tree.command(name="download", description="Add track to playlist")
        async def download(interaction: discord.Interaction, url: str):
            if not interaction.response.is_done():
                await interaction.response.defer()

            try:
                await interaction.followup.send("Downloading track...")
                self.logger.info(f"[/download] Downloading track from URL: {url}")

                response = requests.get(f"http://localhost:52401/Downloader/DownloadTrack", params={"url": url})
                if response.status_code != 200:
                    self.logger.error(f"[/download] Failed to download track. HTTP {response.status_code}: {response.text}")
                    await interaction.followup.send(f"Failed to download track: {response.text}")
                    return

                await interaction.followup.send("Track downloaded successfully!")
                self.logger.info("[/download] Track downloaded successfully!")
            except requests.RequestException as e:
                self.logger.error(f"[/download] HTTP request error: {e}")
                await interaction.followup.send(f"Failed to download track: {e}")
            except Exception as e:
                self.logger.error(f"[/download] Unexpected error: {e}")
                await interaction.followup.send(f"Failed to download track: {e}")

        @self.bot.tree.command(name="shuffle", description="Shuffle the playlist")
        async def shuffle(interaction: discord.Interaction, mode: str):
            try:
                if not interaction.response.is_done():
                    await interaction.response.defer()

                if mode not in ["t", "f"]:
                    await interaction.followup.send("Invalid mode. Please use 't' or 'f'.")
                    return

                response = requests.post(f"http://127.0.0.1:58912/api/Playlist/shuffle", params={"mode": mode})
                if response.status_code != 200:
                    self.logger.error(f"[/shuffle] Failed to set shuffle mode. HTTP {response.status_code}: {response.text}")
                    await interaction.followup.send(f"Failed to set shuffle mode: {response.text}")
                    return

                await interaction.followup.send(f"Shuffle mode is now {mode}.")
                self.logger.info(f"[/shuffle] Shuffle mode set to {mode}.")

            except requests.RequestException as e:
                self.logger.error(f"[/shuffle] HTTP request error: {e}")
                await interaction.followup.send(f"Failed to set shuffle mode: {e}")
            except Exception as e:
                self.logger.error(f"[/shuffle] Unexpected error: {e}")
                await interaction.followup.send(f"Failed to set shuffle mode: {e}")



        @self.bot.tree.command(name="repeat", description="Set repeat mode: 0 - none, 1 - single track, 2 - all tracks")
        async def repeat(interaction: discord.Interaction, mode: int):
            if not interaction.response.is_done():
                await interaction.response.defer()

            if not isinstance(mode, int) or mode not in [0, 1, 2]:
                await interaction.followup.send("Invalid repeat mode. Use 0, 1, or 2.")
                return

            try:
                response = requests.post(f"http://127.0.0.1:58912/api/Playlist/repeat", params={"mode": mode})
                if response.status_code != 200:
                    self.logger.error(f"[/repeat] Failed to set repeat mode. HTTP {response.status_code}: {response.text}")
                    await interaction.followup.send(f"Failed to set repeat mode: {response.text}")
                    return

                await interaction.followup.send(f"Repeat mode set to {mode}.")
                self.logger.info(f"[/repeat] Repeat mode set to {mode}.")

            except requests.RequestException as e:
                self.logger.error(f"[/repeat] HTTP request error: {e}")
                await interaction.followup.send(f"Failed to set repeat mode: {e}")
            except Exception as e:
                self.logger.error(f"[/repeat] Unexpected error: {e}")
                await interaction.followup.send(f"Failed to set repeat mode: {e}")



    def run(self):
        try:
            self.bot.run(self.token)
        except Exception as e:
            self.logger.critical(f"[run] Critical error: {e}")
