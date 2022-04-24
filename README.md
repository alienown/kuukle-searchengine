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

## Used technologies:
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

## Architecture

- Model extractor: extracts data from 20 Newsgroups and BBC News datasets, inserts documents to SQL Server database, and creates model that consists of text vectors  used by ranking API to calculate similarity between query and documents
- Data layer: it is a SQL Server database which stores document information like title, body, and category 
- Ranking API: Python Flask REST API that returns the most similar documents to query in request
- Service layer: a bridge between presentation layer and API & database, defines POCO data transfer objects 
- Presentation layer: an ASP .NET Core MVC web applciation that serves front-end to end-user

![image](https://user-images.githubusercontent.com/47573956/164945924-0021252e-bbf8-41c0-bc0a-474bc3112312.png)

## Usage:
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

## Document ranking algorithm implementation details:
The techniques used to implement ranking algorithm are based on text vectorization. From two datasets each document is represented as vector of numbers. Using the same techniques to transform query to vector, it is easy to calculate similarity measures between documents and query and pick the most relevant results.

### Preprocessing
Before proceeding to text vectorization, each document has been prepared in special manner. Each document has been cleaned out off punctuations and special signs like "@", "!", etc. The text was also lowercased. Then documents were lemmatized. Words that don't represent any semantic value, but are used only for grammatic correctness were also removed. The example of these words are: "at", "a", "the", "is", "are", etc. This set of words is called stopwords. Prepared documents were saved in pandas dataframe. The example of prepared document is presented on image below.

![image](https://user-images.githubusercontent.com/47573956/164947560-f1250616-af70-461b-b766-938b5570e6b4.png)

### Creating documents vector representation
Each document is represented by 3 vectors: title vector, body vector, and semantic vector. For similarity comparison between document and query, the algorithm uses TF-IDF for literal comparison and Latent semantic analysis (LSA - https://en.wikipedia.org/wiki/Latent_semantic_analysis) for semantic comparison.

#### TF-IDF
Title and body vectors are TF-IDF vectors created using columns "Cleaned title", "Cleaned title lemmatized", "Cleaned body", and "Cleaned body lemmatized" from prepared documents dataframe mentioned in [Preprocessing](#preprocessing) stage.
TF-IDF vectors contain stopwords. Oftentimes words like "where", "I'm" are present in document titles so they could be used for achieving better result relevance.

After computing TF-IDF, the dictionary contains 151442 unique words.

![image](https://user-images.githubusercontent.com/47573956/164983598-d583aad7-11e7-4ea4-9547-6e7c847a029e.png)

That means that each TF-IDF vector is 151442 long.

#### Latent semantic analysis
LSA technique allows for identifying interesting patterns between words like synonymy. Using LSA it is possible to compare documents based on their semantic similarity. This is a good addition to TF-IDF literal comparison which can boost query result relevance to end-user. In this project LSA is implemented using
Singular Value Decomposition (SVD - https://en.wikipedia.org/wiki/Singular_value_decomposition), to be more specific - Truncated SVD. Truncated SVD allows for dimensionality reduction. When reducing vector dimensionality, it is possible to uncover interesting patterns between words.

To create semantic vectors cleaned lemmatized title and cleaned lemmatized body were used, getting rid of inflectional varieties and stop words, since such phrases usually have no semantic value. Truncated SVD was applied to TF-IDF vectors created from title and body contents, reducing TF-IDF vectors dimensionality to 25. Although no evaluation step was carried on in this project to confirm that this number performs best, the number 25 was chosen because there are 25 different categories - each with it's own meaning.

It is worth to notice that by using SVD not only document vectors are created but also vectors for individual words. That means that it is also possible to check how much a given word is correlated with 25 categories by looking at it's vector.

To show LSA effects, for each category, documents belonging to it were averaged out and visualised on 2D plane using UMAP algorithm (https://umap-learn.readthedocs.io/en/latest/). Categories like "rec.sport.baseball", "sport" or "rec.sport.hockey" are about sports and are close to each other. It is surprising (or maybe not really?) that religous categories ("talk.religion.misc" or "c.religion.christian") are close to politics topics.

![image](https://user-images.githubusercontent.com/47573956/164984395-2fbed0a7-3dc1-4147-8281-2e04cee50d30.png)

### Query autocorrection
The algorithm can do simple query correction if the word given by the user doesn't exist in TF-IDF words dictionary created in [TF-IDF](#tf-idf). Autocorrection is based on SymSpellPy library that uses Damerau–Levenshtein distance (https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance).

For example, for query "manheszter junaited" the algorithm suggests "manchester united" query instead:

![image](https://user-images.githubusercontent.com/47573956/164985887-c667009c-24b9-4312-a610-8c4837fbdebc.png)

### Calculating similarity between query and documents

The query that is passed to the API with request is prepared in the same manner as documents. Query is cleaned and extended using it's lemmatized form. For example, for query `I was trying to catch a bus!!!` the resulting query will be `i was trying to catch a bus try`.

The similarity between query and documents is an average of three values. Semantic similarity between query and vector, cosine similarity between query TF-IDF vector and document title TF-IDF vector, and cosine similarity between query TF-IDF vector and document body TF-IDF vector. Body TF-IDF similarity is weighted using semantic similarity. In case of low semantic similarity, the authors believe that the content of document should have less impact on final result. Given that, the similarity is computed using given formula that combines literal and semantic similarity in final score:

![image](https://user-images.githubusercontent.com/47573956/164987053-85d596e2-62f9-4d76-ac73-753a4a02c7e0.png)

The query semantic vector is obtained by averaging semantic vectors of individual words in query. The semantic similarity is computed using given formula:

![image](https://user-images.githubusercontent.com/47573956/164987065-bb34fc38-1e10-438d-bfcc-c986f101c233.png)

Including cosine similarity between category semantic vector and query semantic vector seemed to boost result relevance. For example, before including this variable, when querying for "manchester united", the result set contained some politics documents about city Manchester. Including category semantic similarity reduced this problem.

After computing similarities, documents are sorted in descending order based on final score. Top *n* documents are returned to end-user where *n* is a parameter passed in a request to the API.

## Future work

Although it was not a scope of this project it is essential to notice that implemented algorithm requires to carry out an evaluation process that checks at which parameters the algorithm performs best. Also different algorithms for text vectorization could be tested, like Word2vec (https://en.wikipedia.org/wiki/Word2vec) or GloVe (https://nlp.stanford.edu/projects/glove/)
