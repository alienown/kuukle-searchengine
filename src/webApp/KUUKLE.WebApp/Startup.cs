using LinqToDB.AspNet;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using NLP.Data.Data;
using NLP.Models.Models.DocumentDetails;
using NLP.Models.Models.Search;
using NLP.Services.Services.DocumentSearch;

namespace NLPSearchEngine
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllersWithViews();
            this.ConfigureDatabase(services);
            this.ConfigureBusinessServices(services);
            this.ConfigureModels(services);
        }

        private void ConfigureDatabase(IServiceCollection services)
        {
            services.AddLinqToDbContext<AppDataConnection>((provider, options) => {
                options.UseSqlServer(Configuration.GetConnectionString("Default"));
            });
        }

        private void ConfigureModels(IServiceCollection services)
        {
            services.AddScoped<ISearchModel, SearchModel>();
            services.AddScoped<IDocumentDetailsModel, DocumentDetailsModel>();
        }

        private void ConfigureBusinessServices(IServiceCollection services)
        {
            services.AddScoped<IDocumentService, DocumentService>();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Home/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }
            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseRouting();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=Index}/{id?}");
            });
        }
    }
}
