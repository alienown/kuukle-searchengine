using NLP.Services.Services.DocumentSearch;
using System;
using System.Threading.Tasks;

namespace NLP.Models.Models.Search
{
    public class SearchModel : ISearchModel
    {
        private readonly IDocumentService documentService;

        public SearchModel(IDocumentService documentService)
        {
            this.documentService = documentService;
        }

        public SearchViewModel GetSearchViewModel(string query = null, int pageNumber = 1, bool forceQuery = false)
        {
            var viewModel = new SearchViewModel
            {
                Query = query,
                PageNumber = pageNumber,
                ForceQuery = forceQuery,
            };

            return viewModel;
        }

        public async Task<SearchResultViewModel> GetDocuments(string query = null, int pageNumber = 1, bool forceQuery = false)
        {
            var watch = System.Diagnostics.Stopwatch.StartNew();
            var searchResult = await this.documentService.GetDocuments(query, pageNumber, forceQuery);
            watch.Stop();
            var elapsedMilliseconds = watch.ElapsedMilliseconds;

            if (!string.IsNullOrWhiteSpace(query))
            {
                foreach (var document in searchResult.Documents)
                {
                    document.Score = Math.Round(document.Score.Value * 100, 2);
                    document.TitleScore = Math.Round(document.TitleScore.Value * 100, 2);
                    document.BodyScore = Math.Round(document.BodyScore.Value * 100, 2);
                    document.SemanticScore = Math.Round(document.SemanticScore.Value * 100, 2);
                }
            }

            var result = new SearchResultViewModel
            {
                Documents = searchResult.Documents,
                Total = searchResult.Total,
                SuggestedQuery = searchResult.SuggestedQuery,
                SearchTime = Math.Round((decimal)(elapsedMilliseconds / 1000.0), 2),
            };

            return result;
        }
    }
}
