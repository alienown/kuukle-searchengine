using Microsoft.AspNetCore.Mvc;
using NLP.Models.Models.DocumentDetails;
using NLP.Models.Models.Search;
using System.Threading.Tasks;

namespace NLPSearchEngine.Controllers
{
    public class HomeController : Controller
    {
        private readonly ISearchModel searchModel;
        private readonly IDocumentDetailsModel documentDetailsModel;

        public HomeController(ISearchModel searchModel, IDocumentDetailsModel documentDetailsModel)
        {
            this.searchModel = searchModel;
            this.documentDetailsModel = documentDetailsModel;
        }

        [HttpGet]
        public IActionResult Index()
        {
            return View();
        }

        [HttpGet]
        public IActionResult Search(string query = null, int pageNumber = 1, bool forceQuery = false)
        {
            var viewModel = this.searchModel.GetSearchViewModel(query, pageNumber, forceQuery);
            return View(viewModel);
        }

        [HttpGet]
        public async Task<IActionResult> GetDocuments(string query = null, int pageNumber = 1, bool forceQuery = false)
        {
            var searchResult = await this.searchModel.GetDocuments(query, pageNumber, forceQuery);
            return PartialView("_Documents", searchResult);
        }

        [HttpGet]
        public async Task<IActionResult> Details(long id)
        {
            var viewModel = await this.documentDetailsModel.GetDocument(id);
            return View(viewModel);
        }
    }
}
