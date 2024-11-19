using MagicBard.DownloaderAPI.Services;
using MagicBard.DownloaderAPI.Settings;

namespace MagicBard.DownloaderAPI
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Чтение настроек из конфигурации
            var serverSettings = builder.Configuration.GetSection("ServerSettings").Get<ServerSettings>();
            var swaggerSettings = builder.Configuration.GetSection("SwaggerSettings").Get<SwaggerSettings>();

            builder.Services.AddScoped<IDownloaderService, DownloaderService>();

            // Добавляем сервисы
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            // Настройка, чтобы приложение слушало только на localhost и на порту 5201
            app.Urls.Add(serverSettings.Url);

            // Настройка Swagger (будет работать всегда)
            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint(swaggerSettings.SwaggerEndpoint, "Downloader API V1");
                c.RoutePrefix = swaggerSettings.SwaggerAddress;
            });

            app.UseHttpsRedirection();
            app.UseAuthorization();
            app.MapControllers();

            app.Run();
        }
    }
}
