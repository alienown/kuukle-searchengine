# Kuukle - Simple Search Engine
This project was created for Natural Language Processing course. The purpose of the project was to implement simple document search engine using text vectorization techniques. Created project consists of a front-end web application written in ASP .NET Core. Web application communicates with document ranking API written in Python.

Credits to https://github.com/MefjuEs for help in creating this project.

Search engine allows for searching documents from two corporas:
- BBC News - http://mlg.ucd.ie/datasets/bbc.html
- 20 Newsgroups - http://qwone.com/~jason/20Newsgroups/

Main view, enter query and click *Search* to search for documents

![image](https://user-images.githubusercontent.com/47573956/164914876-25cb768b-51c7-49bd-979f-6faf47f00af2.png)

Displaying search results for "mencester unted" query. In similar fashion to Google search engine, application also checks for errors in provided query and displays results for corrected query. Documents are ranked based on query literal similarity to document's title and body, and also semantic similarity.

![image](https://user-images.githubusercontent.com/47573956/164914933-7232bea4-7725-48ef-aeea-4c6ac15d7b76.png)

### Used technologies:
- ASP.NET Core MVC - https://docs.microsoft.com/en-us/aspnet/core/mvc/overview?view=aspnetcore-3.1 - used to build web application that serves front-end to end user
- JavaScript, jQuery - https://developer.mozilla.org/en-US/docs/Web/JavaScript, https://jquery.com/ - used to build front-end logic between user and components rendered on website 
- RestSharp - https://restsharp.dev/ - .NET library for communication between ASP.NET Core MVC application and documents ranking API
- Linq2DB - https://github.com/linq2db/linq2db - C# database access library used for retrieving documents content
- SQL Server - https://www.microsoft.com/en-us/sql-server/sql-server-2019 - MS SQL Server DBMS was used for storing documents data
- Python - https://www.python.org/ - Python language with its great math libraries was used for implementing document ranking algorithm and building web API serving documents ranking
- Jupyter Notebook - https://jupyter.org/ - great tool used for implementing and testing performance of algorithms before moving them to production, used for implementing and testing documents ranking algorithm
- Flask - https://flask.palletsprojects.com/en/2.1.x/ - python library used for implementing document ranking web API in JSON format
- Sklearn - https://scikit-learn.org/stable/ - python library used for document text vectorization
- Spacy - https://spacy.io/ - python Natural Language Processing library used for text tokenization and lemmatization
- Pandas - https://pandas.pydata.org/ - powerful data analysis and manipulation tool, built on top of the Python programming language
- SymSpellPy - https://github.com/mammothb/symspellpy - Python port of https://github.com/wolfgarbe/SymSpell, used for spelling correction

### Configuration & Installation:
1. Run `src/webApp/KUUKLE.Data/dbscript.sql` in SQL Server DBMS. This creates documents database
2. Download BBC News dataset from http://mlg.ucd.ie/datasets/bbc.html. Copy and pase downloaded directory to `src/docsApi/extractor`. You don't need to download 20 Newsgroups dataset manually beacuse it is fetched from remote endpoint automatically by extractor
3. Edit `src/docsApi/extractor/config.json`. In field "dbConnectionString" enter connection string of the database you've created in 1. This is where extractor will save prepared documents content
4. Open your cmd inside `src/docsApi/extractor` and run `pip install -r requirements.txt`. This will install required dependencies for extractor
5. Run `src/docsApi/extractor/extractor.py`, this can take several minutes
6. Go to `src/docsApi/api` and run `pip install -r requirements.txt`. This will install required dependencies for documents API
7. This step is optional. You can change API url in `app.py`
8. In `src/webApp/KUUKLE.WebApp/appsettings.Development.json` enter database connection string and ranking API url if you've changed it in 7. Do it in the following sections:
```
{
  ...
  "ConnectionStrings": {
    "Default": "ENTER CONNECTION STRING HERE"
  },
  "DocsApiUrl": "ENTER DOCUMENT RANKING API URL HERE"
  ...
}
```
10. In `src/webApp/KUUKLE.WebApp` run `dotnet run`. Web application should build and start

### Document ranking algorithm implementation details:
