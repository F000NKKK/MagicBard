public class Track
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N").Substring(0, 12);
    public string Title { get; set; } = string.Empty;
    public string Time { get; set; } = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
    public string Path { get; set; } = string.Empty;
}
