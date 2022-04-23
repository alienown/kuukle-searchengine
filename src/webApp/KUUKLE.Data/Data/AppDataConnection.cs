using LinqToDB;
using LinqToDB.Configuration;
using LinqToDB.Data;
using KUUKLE.Data.Domain;

namespace KUUKLE.Data.Data
{
    public class AppDataConnection : DataConnection
    {
        public ITable<Document> Document => GetTable<Document>();
        public ITable<DocumentCategory> DocumentCategory => GetTable<DocumentCategory>();
        public ITable<DocumentSource> DocumentSource => GetTable<DocumentSource>();

        public AppDataConnection(LinqToDbConnectionOptions<AppDataConnection> options)
           : base(options)
        {

        }
    }
}
