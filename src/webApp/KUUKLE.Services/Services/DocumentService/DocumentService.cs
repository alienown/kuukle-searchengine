using LinqToDB;
using Microsoft.Extensions.Configuration;
using NLP.Data.Data;
using RestSharp;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace NLP.Services.Services.DocumentSearch
{
    public class DocumentService : IDocumentService
    {
        private readonly int pageSize = 10;

        private readonly AppDataConnection dbConnection;
        private readonly IConfiguration configuration;

        public DocumentService(AppDataConnection dbConnection, IConfiguration configuration)
        {
            this.dbConnection = dbConnection;
            this.configuration = configuration;
        }

        public async Task<DocumentSearchResult> GetDocuments(string query = null, int pageNumber = 1, bool forceQuery = false)
        {
            var result = new DocumentSearchResult();

            if (!string.IsNullOrWhiteSpace(query))
            {
                var response = await this.FetchDocumentsFromAPI(query, pageNumber, forceQuery);
                var scoredDocumentsIds = response.Documents.Select(x => x.Id).ToList();
                var documents = await this.FetchDocumentsFromDatabase(scoredDocumentsIds, pageNumber);
                this.FillDocumentsWithScores(documents, response.Documents);
                documents = documents.OrderByDescending(x => x.Score).ToList();

                result.Documents = documents;
                result.Total = response.Total;
                result.SuggestedQuery = response.SuggestedQuery;
            }
            else
            {
                var documents = await this.FetchDocumentsFromDatabase(pageNumber: pageNumber);
                var total = await this.GetDocumentsCount();

                result.Documents = documents;
                result.Total = total;
            }

            return result;
        }

        private async Task<List<Document>> FetchDocumentsFromDatabase(List<long> ids = null, int pageNumber = 1)
        {
            var query = from document in dbConnection.Document
                        from category in dbConnection.DocumentCategory.Where(x => x.Id == document.CategoryId)
                        from source in dbConnection.DocumentSource.Where(x => x.Id == document.SourceId)
                        select new
                        {
                            Id = document.Id,
                            Category = category.Name,
                            Source = source.Name,
                            Title = document.Title,
                            BodyPreview = document.Body.Substring(0, 300),
                        };

            if (ids != null)
            {
                query = query.Where(x => ids.Contains(x.Id));
            }
            else
            {
                query = query.Skip(this.pageSize * (pageNumber - 1)).Take(this.pageSize);
            }

            var queryResult = await query.ToListAsync();

            var result = new List<Document>();

            foreach (var dbDoc in queryResult)
            {
                var viewModel = new Document
                {
                    Id = dbDoc.Id,
                    Category = dbDoc.Category,
                    Source = dbDoc.Source,
                    Title = dbDoc.Title,
                    Body = dbDoc.BodyPreview,
                };

                result.Add(viewModel);
            }

            return result;
        }

        private void FillDocumentsWithScores(List<Document> documentDTOs, List<DocumentScore> scoreDTOs)
        {
            if (documentDTOs.Any())
            {
                var documentIdsToScores = scoreDTOs.ToDictionary(x => x.Id);
                foreach (var document in documentDTOs)
                {
                    var score = documentIdsToScores[document.Id];
                    document.TitleScore = score.TitleScore;
                    document.BodyScore = score.BodyScore;
                    document.SemanticScore = score.SemanticScore;
                    document.Score = score.Score;
                }
            }
        }

        private async Task<ScoreResponse> FetchDocumentsFromAPI(string query, int pageNumber, bool forceQuery)
        {
            var baseUrl = this.configuration["DocsApiUrl"];

            var client = new RestClient(baseUrl);

            var request = new RestRequest("/documents")
                .AddParameter("query", query)
                .AddParameter("pageNumber", pageNumber)
                .AddParameter("forceQuery", forceQuery);

            var result = await client.GetAsync<ScoreResponse>(request);

            return result;
        }

        private async Task<long> GetDocumentsCount()
        {
            var count = await this.dbConnection.Document.CountAsync();
            return count;
        }

        public async Task<Document> GetDocument(long id)
        {
            var details = await (from document in dbConnection.Document
                                 from category in dbConnection.DocumentCategory.Where(x => x.Id == document.CategoryId)
                                 from source in dbConnection.DocumentSource.Where(x => x.Id == document.SourceId)
                                 select new Document
                                 {
                                     Id = document.Id,
                                     Category = category.Name,
                                     Source = source.Name,
                                     Title = document.Title,
                                     Body = document.Body,
                                 }).FirstOrDefaultAsync(x => x.Id == id);

            return details;
        }
    }
}
