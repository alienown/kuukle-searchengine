using NLP.Services.Services.DocumentSearch;
using System.Threading.Tasks;

namespace NLP.Models.Models.DocumentDetails
{
    public interface IDocumentDetailsModel
    {
        Task<Document> GetDocument(long id);
    }
}
