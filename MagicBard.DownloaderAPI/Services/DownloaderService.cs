using MagicBard.DownloaderAPI.Settings;
using Microsoft.Extensions.Options;
using System.Diagnostics;

namespace MagicBard.DownloaderAPI.Services
{

    public class DownloaderService : IDownloaderService
    {
        private readonly DownloaderSettings _settings;
        private readonly ILogger<DownloaderService> _logger;

        public DownloaderService(IOptions<DownloaderSettings> options, ILogger<DownloaderService> logger)
        {
            _settings = options.Value;
            _logger = logger;

            // Validate yt-dlp path
            if (!File.Exists(_settings.YtDlpPath))
            {
                _logger.LogError("The file {Path} was not found or is not an executable file.", _settings.YtDlpPath);
                throw new FileNotFoundException($"The file {_settings.YtDlpPath} was not found or is not an executable file.");
            }

            // Ensure download path exists
            if (!Directory.Exists(_settings.DownloadPath))
            {
                Directory.CreateDirectory(_settings.DownloadPath);
            }
        }

        public async Task<string?> DownloadTrackAsync(string url)
        {
            try
            {
                _logger.LogInformation("Starting download for URL: {Url}", url);

                var process = await Task.Run(() => Process.Start(new ProcessStartInfo
                {
                    FileName = _settings.YtDlpPath,
                    Arguments = url,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    WorkingDirectory = _settings.DownloadPath,
                    CreateNoWindow = true
                }));

                if (process == null) throw new Exception("Failed to start yt-dlp process.");

                await process.WaitForExitAsync();

                if (process.ExitCode != 0)
                {
                    var error = await process.StandardError.ReadToEndAsync();
                    _logger.LogError("Download failed: {Error}", error);
                    throw new Exception(error);
                }

                var output = await process.StandardOutput.ReadToEndAsync();
                var destinationLine = output.Split("\n").FirstOrDefault(line => line.Contains("[download] Destination:"));

                if (destinationLine != null)
                {
                    var filePath = destinationLine.Split(": ", 2)[1].Trim();
                    _logger.LogInformation("Download completed: {FilePath}", filePath);
                    return filePath;
                }

                throw new Exception("File destination not found in output.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error downloading track.");
                return null;
            }
        }
    }
}