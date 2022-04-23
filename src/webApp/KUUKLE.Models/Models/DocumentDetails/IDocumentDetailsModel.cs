using KUUKLE.Services.Services.DocumentSearch;
using System.Threading.Tasks;

namespace KUUKLE.Models.Models.DocumentDetails
{
    public interface IDocumentDetailsModel
    {
        Task<Document> GetDocument(long id);
    }
}
