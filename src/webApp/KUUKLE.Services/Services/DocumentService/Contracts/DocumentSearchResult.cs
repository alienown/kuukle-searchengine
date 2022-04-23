using System.Collections.Generic;

namespace NLP.Services.Services.DocumentSearch
{
    public class DocumentSearchResult
    {
        public List<Document> Documents { get; set; }

        public long Total { get; set; }

        public string SuggestedQuery { get; set; }
    }
}
