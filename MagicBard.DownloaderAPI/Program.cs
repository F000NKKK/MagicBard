using MagicBard.DownloaderAPI.Services;
using MagicBard.DownloaderAPI.Settings;

namespace MagicBard.DownloaderAPI
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // ������ �������� �� ������������
            var serverSettings = builder.Configuration.GetSection("ServerSettings").Get<ServerSettings>();
            var swaggerSettings = builder.Configuration.GetSection("SwaggerSettings").Get<SwaggerSettings>();

            builder.Services.AddScoped<IDownloaderService, DownloaderService>();

            // ��������� �������
            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            // ���������, ����� ���������� ������� ������ �� localhost � �� ����� 5201
            app.Urls.Add(serverSettings.Url);

            // ��������� Swagger (����� �������� ������)
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
