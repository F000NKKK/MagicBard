namespace MagicBard.PlaylistAPI.Services
{
    public interface IPlaylistService
    {
        List<Track> GetPlaylist();
        Track GetCurrentTrack();
        Track GetNextTrack();
        void ShufflePlaylist(string mode);
        void SetRepeatMode(int mode);
        void LoadTracks();
        void SavePlaylist();
        void UpdatePlaylist();
    }
}