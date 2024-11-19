using Newtonsoft.Json;
using System.IO.Abstractions;

namespace MagicBard.PlaylistAPI
{
    public class PlaylistService : IPlaylistService, IHostedService
    {
        private readonly string PlaylistFolder;
        private readonly string PlaylistFile;
        private readonly ILogger<PlaylistService> _logger;
        private readonly IFileSystem _fileSystem;

        private List<Track> Playlist { get; set; } = new();
        private List<Track> OriginalOrder { get; set; } = new();
        private int CurrentIndex { get; set; } = 0;
        private int RepeatMode { get; set; } = 0;

        private CancellationTokenSource _cancellationTokenSource;
        private Task _backgroundTask;

        public PlaylistService(IConfiguration configuration, ILogger<PlaylistService> logger, IFileSystem fileSystem)
        {
            PlaylistFolder = configuration.GetValue<string>("AppSettings:PlaylistFolder") ?? "/playlist";
            PlaylistFile = configuration.GetValue<string>("AppSettings:PlaylistFile") ?? "playlist.json";
            _logger = logger;
            _fileSystem = fileSystem;

            _logger.LogInformation($"Playlist folder: {PlaylistFolder}");

            LoadTracks();
        }

        public Task StartAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Playlist service started.");

            _cancellationTokenSource = new CancellationTokenSource();
            _backgroundTask = Task.Run(() => BackgroundTask(_cancellationTokenSource.Token), cancellationToken);

            return Task.CompletedTask;
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Playlist service stopping.");

            _cancellationTokenSource.Cancel();
            return _backgroundTask ?? Task.CompletedTask;
        }

        private async Task BackgroundTask(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    UpdatePlaylist();
                    await Task.Delay(TimeSpan.FromSeconds(10), token); // Обновляем плейлист каждые 10 сек
                }
                catch (Exception ex)
                {
                    _logger.LogError($"Error in background task: {ex.Message}");
                }
            }
        }

        public void LoadTracks()
        {
            if (_fileSystem.File.Exists(PlaylistFile))
            {
                var json = _fileSystem.File.ReadAllText(PlaylistFile);
                Playlist = JsonConvert.DeserializeObject<List<Track>>(json) ?? new List<Track>();
                _logger.LogInformation("Playlist loaded from file.");
            }
            else
            {
                Playlist = _fileSystem.Directory
                    .EnumerateFiles(PlaylistFolder)
                    .Where(filePath => IsSupportedFileExtension(filePath))
                    .Select(filePath => new Track
                    {
                        Title = Path.GetFileNameWithoutExtension(filePath),
                        Path = Path.GetFileName(filePath)
                    })
                    .ToList();
                SavePlaylist();
                _logger.LogInformation("Playlist created from folder files.");
            }

            OriginalOrder = new List<Track>(Playlist);
        }

        private bool IsSupportedFileExtension(string filePath)
        {
            var supportedExtensions = new[] { ".mp3", ".wav", ".webm", ".flac" };
            return supportedExtensions.Contains(Path.GetExtension(filePath).ToLower());
        }

        public void SavePlaylist()
        {
            var json = JsonConvert.SerializeObject(Playlist, Formatting.Indented);
            _fileSystem.File.WriteAllText(PlaylistFile, json);
            _logger.LogInformation("Playlist saved to file.");
        }

        public void UpdatePlaylist()
        {
            var folderFiles = new HashSet<string>(
                _fileSystem.Directory.GetFiles(PlaylistFolder)
                    .Where(filePath => IsSupportedFileExtension(filePath))
                    .Select(filePath => Path.GetFileName(filePath))
            );

            _logger.LogInformation($"Files in folder: {string.Join(", ", folderFiles)}");

            var playlistFiles = new HashSet<string>(Playlist.Select(t => t.Path));

            _logger.LogInformation($"Files in playlist: {string.Join(", ", playlistFiles)}");

            var newFiles = folderFiles.Except(playlistFiles);
            _logger.LogInformation($"New files to add: {string.Join(", ", newFiles)}");

            foreach (var fileName in newFiles)
            {
                var newTrack = new Track
                {
                    Title = Path.GetFileNameWithoutExtension(fileName),
                    Path = fileName
                };
                Playlist.Add(newTrack);
                OriginalOrder.Add(newTrack);
                _logger.LogInformation($"New track added: {newTrack.Title}");
            }

            Playlist = Playlist.Where(track => folderFiles.Contains(track.Path)).ToList();
            OriginalOrder = OriginalOrder.Where(track => folderFiles.Contains(track.Path)).ToList();

            _logger.LogInformation($"Updated playlist: {string.Join(", ", Playlist.Select(t => t.Title))}");

            SavePlaylist();
        }

        public List<Track> GetPlaylist() => Playlist;

        public Track GetCurrentTrack()
        {
            if (!Playlist.Any())
            {
                _logger.LogWarning("Playlist is empty.");
                throw new InvalidOperationException("Playlist is empty.");
            }
            return Playlist[CurrentIndex];
        }

        public Track GetNextTrack()
        {
            if (!Playlist.Any())
            {
                _logger.LogWarning("Playlist is empty.");
                throw new InvalidOperationException("Playlist is empty.");
            }

            if (RepeatMode == 0 && CurrentIndex + 1 == Playlist.Count)
            {
                _logger.LogInformation("End of the playlist.");

                CurrentIndex += 1;
                var LastIndex = (CurrentIndex + 1) % Playlist.Count;
                return Playlist[LastIndex];
            }
            else if(RepeatMode == 0 && CurrentIndex == Playlist.Count)
            {
                CurrentIndex = 0;
                return new Track();
            }

            if (RepeatMode == 1)
            {
                _logger.LogInformation("Repeat current track.");
                return Playlist[CurrentIndex];
            }

            CurrentIndex = (CurrentIndex + 1) % Playlist.Count;

            if (RepeatMode == 2 && CurrentIndex == 0)
            {
                _logger.LogInformation("Repeat playlist.");
                CurrentIndex = 0;
            }

            return Playlist[CurrentIndex];
        }

        public void ShufflePlaylist(string mode)
        {
            if (mode == "t")
            {
                Playlist = Playlist.OrderBy(_ => Guid.NewGuid()).ToList();
                CurrentIndex = 0;
                _logger.LogInformation("Playlist shuffled randomly.");
            }
            else if (mode == "f")
            {
                Playlist = new List<Track>(OriginalOrder);
                CurrentIndex = 0;
                _logger.LogInformation("Playlist restored to original order.");
            }
            else
            {
                _logger.LogWarning("Invalid shuffle mode.");
                throw new ArgumentException("Invalid mode. Use 't' or 'f'");
            }

            SavePlaylist();
        }

        public void SetRepeatMode(int mode)
        {
            if (mode < 0 || mode > 2)
            {
                _logger.LogWarning("Invalid repeat mode.");
                throw new ArgumentException("Invalid mode. Use '0', '1', or '2'");
            }

            RepeatMode = mode;
            _logger.LogInformation($"Repeat mode set to {RepeatMode}");
        }
    }
}
