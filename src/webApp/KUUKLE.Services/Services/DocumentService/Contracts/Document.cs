namespace KUUKLE.Services.Services.DocumentSearch
{
    public class Document
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Category { get; set; }
        public string Source { get; set; }
        public string Body { get; set; }
        public double? TitleScore { get; set; }
        public double? BodyScore { get; set; }
        public double? SemanticScore { get; set; }
        public double? Score { get; set; }
    }
}
