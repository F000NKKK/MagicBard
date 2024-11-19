using Newtonsoft.Json;
using Microsoft.OpenApi.Models;
using System.Net;
using MagicBard.PlaylistAPI;
using System.IO.Abstractions;
internal class Program
{
    private static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);


        builder.Services.AddSingleton<IFileSystem, FileSystem>();
        builder.Services.AddSingleton<IPlaylistService, PlaylistService>();
        builder.Services.AddHostedService<PlaylistService>();

        builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

        builder.Services.AddControllers()
            .AddNewtonsoftJson(options =>
            {
                options.SerializerSettings.Formatting = Formatting.Indented;
                options.SerializerSettings.NullValueHandling = NullValueHandling.Ignore;
            });

        builder.WebHost.ConfigureKestrel(options =>
        {
            var ipAddress = builder.Configuration.GetValue<string>("AppSettings:IpAddress");
            var httpPort = builder.Configuration.GetValue<int>("AppSettings:HttpPort");

            if (string.IsNullOrEmpty(ipAddress))
            {
                throw new ArgumentNullException("AppSettings:IpAddress", "IP address is not provided in configuration.");
            }

            options.Listen(IPAddress.Parse(ipAddress), httpPort);
        });

        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen(c =>
        {
            c.SwaggerDoc("v1", new OpenApiInfo
            {
                Title = "Playlist API",
                Version = "v1",
                Description = "API for managing playlists"
            });
        });

        var app = builder.Build();

        app.UseRouting();


        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            var swaggerAddress = builder.Configuration.GetValue<string>("AppSettings:SwaggerAddress");
            var swaggerEndpoint = builder.Configuration.GetValue<string>("AppSettings:SwaggerEndpoint");

            c.SwaggerEndpoint(swaggerEndpoint, "Playlist API V1");
            c.RoutePrefix = swaggerAddress;
        });

        app.MapControllers();
        app.Run();
    }
}
