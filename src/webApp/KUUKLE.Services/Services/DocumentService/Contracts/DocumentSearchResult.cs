using System.Collections.Generic;

namespace KUUKLE.Services.Services.DocumentSearch
{
    public class DocumentSearchResult
    {
        public List<Document> Documents { get; set; }

        public long Total { get; set; }

        public string SuggestedQuery { get; set; }
    }
}
