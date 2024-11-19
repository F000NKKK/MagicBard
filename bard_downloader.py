import asyncio
import os
import logging

class Downloader:
    def __init__(self, yt_dlp_path, download_path, logger):
        self.logger = logger
        self.yt_dlp_path = yt_dlp_path
        self.download_path = download_path

        # Validate yt-dlp path
        if not os.path.isfile(self.yt_dlp_path):
            self.logger.error(f"The file {self.yt_dlp_path} was not found or is not an executable file.")
            raise FileNotFoundError(f"The file {self.yt_dlp_path} was not found or is not an executable file.")

        # Check if the download path exists and create the folder if it does not
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
                self.logger.info(f"Created download folder: {self.download_path}")
            except Exception as e:
                self.logger.error(f"Failed to create download folder: {e}")
                raise PermissionError(f"Failed to create download folder: {e}")

    async def download_track(self, url):
        try:
            self.logger.info(f"Starting track download from URL: {url}")

            # Run the command using asyncio
            process = await asyncio.create_subprocess_exec(
                self.yt_dlp_path,
                url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.download_path
            )

            # Read stdout and stderr
            stdout, stderr = await process.communicate()

            # Logging for debugging
            self.logger.info(f"stdout: {stdout.decode()}")
            self.logger.error(f"stderr: {stderr.decode()}")

            # Check the return code
            if process.returncode != 0:
                error_message = f"Download error: {stderr.decode().strip()}"
                self.logger.error(error_message)
                raise Exception(error_message)

            # Find the line with the file location
            for line in stdout.decode().splitlines():
                if "[download] Destination:" in line:
                    file_path = line.split(": ", 1)[1].strip()
                    self.logger.info(f"Track successfully downloaded: {file_path}")
                    return file_path

            # If file location is not found
            error_message = "Unable to find the file location after downloading."
            self.logger.error(error_message)
            raise Exception(error_message)

        except FileNotFoundError as e:
            self.logger.error(f"Error: {e}")
            return None
        except PermissionError as e:
            self.logger.error(f"Permission error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error while downloading track: {e}", exc_info=True)
            return None


# Example usage
# async def main():
#     downloader = Downloader('./yt-dlp.exe', './playlist', logger)
#     file_path = await downloader.download_track('https://www.youtube.com/watch?v=1ll3FvVk6BA')
#     if file_path:
#         logger.info(f"Track successfully downloaded: {file_path}")
#     else:
#         logger.error("Failed to download the track.")
#
# # Run async code
# asyncio.run(main())
