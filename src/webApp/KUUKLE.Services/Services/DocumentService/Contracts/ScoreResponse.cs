using System.Collections.Generic;

namespace KUUKLE.Services.Services.DocumentSearch
{
    public class ScoreResponse
    {
        public List<DocumentScore> Documents { get; set; }
        public long Total { get; set; }
        public string SuggestedQuery { get; set; }
    }
}
