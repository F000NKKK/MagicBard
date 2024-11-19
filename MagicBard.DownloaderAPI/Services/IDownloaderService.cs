namespace MagicBard.DownloaderAPI.Services;

public interface IDownloaderService
{
    Task<string?> DownloadTrackAsync(string url);
}
