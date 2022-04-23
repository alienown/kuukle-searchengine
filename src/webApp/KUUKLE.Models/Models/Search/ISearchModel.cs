using KUUKLE.Services.Services.DocumentSearch;
using System.Threading.Tasks;

namespace KUUKLE.Models.Models.Search
{
    public interface ISearchModel
    {
        SearchViewModel GetSearchViewModel(string query = null, int pageNumber = 1, bool forceQuery = false);

        Task<SearchResultViewModel> GetDocuments(string query = null, int pageNumber = 1, bool forceQuery = false);
    }
}
