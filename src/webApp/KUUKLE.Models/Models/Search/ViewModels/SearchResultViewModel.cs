using NLP.Services.Services.DocumentSearch;
using System.Collections.Generic;

namespace NLP.Models.Models.Search
{
    public class SearchResultViewModel
    {
        public List<Document> Documents { get; set; }

        public long Total { get; set; }

        public string SuggestedQuery { get; set; }

        public decimal SearchTime { get; set; }
    }
}
