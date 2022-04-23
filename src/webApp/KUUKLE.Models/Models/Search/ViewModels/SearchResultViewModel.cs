using KUUKLE.Services.Services.DocumentSearch;
using System.Collections.Generic;

namespace KUUKLE.Models.Models.Search
{
    public class SearchResultViewModel
    {
        public List<Document> Documents { get; set; }

        public long Total { get; set; }

        public string SuggestedQuery { get; set; }

        public decimal SearchTime { get; set; }
    }
}
