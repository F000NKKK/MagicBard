using MagicBard.DownloaderAPI.Settings;
using Microsoft.Extensions.Options;
using System.Diagnostics;
using System.Text;

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

                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = _settings.YtDlpPath,
                        Arguments = url,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        WorkingDirectory = _settings.DownloadPath,
                        CreateNoWindow = true,
                        UseShellExecute = false
                    },
                    EnableRaisingEvents = true
                };

                var outputBuilder = new StringBuilder();
                var errorBuilder = new StringBuilder();

                process.OutputDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        outputBuilder.AppendLine(e.Data);
                        Console.Write("\r" + e.Data);
                    }
                };

                process.ErrorDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        errorBuilder.AppendLine(e.Data);
                        _logger.LogError("[yt-dlp] {Error}", e.Data);
                    }
                };

                if (!process.Start())
                    throw new Exception("Failed to start yt-dlp process.");

                process.BeginOutputReadLine();
                process.BeginErrorReadLine();

                await process.WaitForExitAsync();

                if (process.ExitCode != 0)
                {
                    throw new Exception($"yt-dlp exited with code {process.ExitCode}: {errorBuilder}");
                }

                _logger.LogInformation("Download completed successfully.");

                // Анализируем вывод для нахождения пути к файлу
                var output = outputBuilder.ToString();
                var destinationLine = output
                    .Split("\n", StringSplitOptions.RemoveEmptyEntries)
                    .FirstOrDefault(line => line.Contains("[download] Destination:"));

                if (destinationLine != null)
                {
                    var filePath = destinationLine.Split(": ", 2)[1].Trim();
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