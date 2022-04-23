using System.Threading.Tasks;

namespace KUUKLE.Services.Services.DocumentSearch
{
    public interface IDocumentService
    {
        Task<DocumentSearchResult> GetDocuments(string query = null, int pageNumber = 1, bool forceQuery = false);

        Task<Document> GetDocument(long id);
    }
}
