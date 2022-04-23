using KUUKLE.Services.Services.DocumentSearch;
using System.Threading.Tasks;

namespace KUUKLE.Models.Models.DocumentDetails
{
    public class DocumentDetailsModel : IDocumentDetailsModel
    {
        private readonly IDocumentService documentService;

        public DocumentDetailsModel(IDocumentService documentService)
        {
            this.documentService = documentService;
        }

        public async Task<Document> GetDocument(long id)
        {
            var document = await this.documentService.GetDocument(id);
            return document;
        }
    }
}
