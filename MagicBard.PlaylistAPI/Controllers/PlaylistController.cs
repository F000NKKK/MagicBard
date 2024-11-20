using MagicBard.PlaylistAPI.Services;
using Microsoft.AspNetCore.Mvc;

namespace MagicBard.PlaylistAPI.Controllers
{

    [ApiController]
    [Route("api/[controller]")]
    public class PlaylistController : ControllerBase
    {
        private readonly IPlaylistService _playlistService;

        public PlaylistController(IPlaylistService playlistService)
        {
            _playlistService = playlistService;
        }

        [HttpGet("tracks")]
        public ActionResult<List<Track>> GetTracks()
        {
            try
            {
                return Ok(_playlistService.GetPlaylist());
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("current")]
        public ActionResult<Track> GetCurrentTrack()
        {
            try
            {
                return Ok(_playlistService.GetCurrentTrack());
            }
            catch (Exception ex)
            {
                return NotFound(new { error = ex.Message });
            }
        }

        [HttpGet("next")]
        public ActionResult<Track> NextTrack()
        {
            try
            {
                return Ok(_playlistService.GetNextTrack());
            }
            catch (Exception ex)
            {
                return NotFound(new { error = ex.Message });
            }
        }

        [HttpPost("shuffle")]
        public IActionResult ShufflePlaylist([FromQuery] string mode = "t")
        {
            try
            {
                _playlistService.ShufflePlaylist(mode);
                return Ok(new { message = $"Shuffle mode set to {mode}", playlist = _playlistService.GetPlaylist() });
            }
            catch (Exception ex)
            {
                return BadRequest(new { error = ex.Message });
            }
        }

        [HttpPost("repeat")]
        public IActionResult SetRepeatMode([FromQuery] int mode)
        {
            try
            {
                _playlistService.SetRepeatMode(mode);
                return Ok(new { repeat_mode = mode });
            }
            catch (Exception ex)
            {
                return BadRequest(new { error = ex.Message });
            }
        }
    }
}