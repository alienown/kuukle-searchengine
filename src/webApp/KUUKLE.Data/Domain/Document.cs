namespace KUUKLE.Data.Domain
{
    public class Document
    {
        public int Id { get; set; }
        public int CategoryId { get; set; }
        public int SourceId { get; set; }
        public string Title { get; set; }
        public string Body { get; set; }
    }
}
