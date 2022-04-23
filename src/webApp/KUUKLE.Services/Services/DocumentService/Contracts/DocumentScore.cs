namespace NLP.Services.Services.DocumentSearch
{
    public class DocumentScore
    {
        public long Id { get; set; }
        public double TitleScore { get; set; }
        public double BodyScore { get; set; }
        public double SemanticScore { get; set; }
        public double Score { get; set; }
    }
}
