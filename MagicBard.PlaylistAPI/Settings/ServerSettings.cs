namespace MagicBard.PlaylistAPI.Settings
{
    public class ServerSettings
    {
        public required string PlaylistFolder { get; set; }
        public required string PlaylistFile { get; set; }
        public required string SwaggerAddress { get; set; }
        public required string SwaggerEndpoint { get; set; }
        public required string IpAddress { get; set; }
        public int HttpPort { get; set; }
    }

}
