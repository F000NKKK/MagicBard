using MagicBard.DownloaderAPI.Services;
using Microsoft.AspNetCore.Mvc;

namespace MagicBard.DownloaderAPI.Controllers;

[ApiController]
[Route("[controller]")]
public class DownloaderController : ControllerBase
{
    private readonly IDownloaderService _downloaderService;
    private readonly ILogger<DownloaderController> _logger;

    public DownloaderController(IDownloaderService downloaderService, ILogger<DownloaderController> logger)
    {
        _downloaderService = downloaderService;
        _logger = logger;
    }

    /// <summary>
    /// Downloads a track from a given URL.
    /// </summary>
    /// <param name="url">The URL of the track to download.</param>
    /// <returns>The path of the downloaded file.</returns>
    [HttpGet("DownloadTrack")]
    public async Task<IActionResult> DownloadTrack([FromQuery] string url)
    {
        if (string.IsNullOrEmpty(url))
        {
            return BadRequest("URL cannot be empty.");
        }

        var result = await _downloaderService.DownloadTrackAsync(url);
        if (result == null)
        {
            return StatusCode(500, "Failed to download track.");
        }

        return Ok(new
        {
            FilePath = result
        });
    }
}
