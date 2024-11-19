using Microsoft.Extensions.Configuration;
using MagicBard.PlaylistAPI.Services;
using System.IO.Abstractions;
using Newtonsoft.Json;
using Microsoft.OpenApi.Models;
using System.Net;
using MagicBard.PlaylistAPI.Settings;

namespace MagicBard.PlaylistAPI
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Чтение конфигурации из appsettings.json
            builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

            // Привязка конфигурации к классу ServerSettings
            builder.Services.Configure<ServerSettings>(builder.Configuration.GetSection("AppSettings"));

            // Регистрация сервисов
            builder.Services.AddSingleton<IFileSystem, FileSystem>();
            builder.Services.AddSingleton<IPlaylistService, PlaylistService>();
            builder.Services.AddHostedService<PlaylistService>();

            // Добавление контроллеров с конфигурацией JSON
            builder.Services.AddControllers()
                .AddNewtonsoftJson(options =>
                {
                    options.SerializerSettings.Formatting = Formatting.Indented;
                    options.SerializerSettings.NullValueHandling = NullValueHandling.Ignore;
                });

            // Настройка Kestrel для прослушивания на нужном IP и порту
            builder.WebHost.ConfigureKestrel((context, options) =>
            {
                var serverSettings = builder.Configuration.GetSection("AppSettings").Get<ServerSettings>();

                if (string.IsNullOrEmpty(serverSettings.IpAddress))
                {
                    throw new ArgumentNullException("AppSettings:IpAddress", "IP address is not provided in configuration.");
                }

                options.Listen(IPAddress.Parse(serverSettings.IpAddress), serverSettings.HttpPort);
            });

            // Настройка Swagger для API
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

            // Настройка маршрутизации и Swagger UI
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
}