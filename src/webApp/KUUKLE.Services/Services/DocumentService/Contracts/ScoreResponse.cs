using System.Collections.Generic;

namespace NLP.Services.Services.DocumentSearch
{
    public class ScoreResponse
    {
        public List<DocumentScore> Documents { get; set; }
        public long Total { get; set; }
        public string SuggestedQuery { get; set; }
    }
}
