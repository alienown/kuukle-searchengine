CREATE DATABASE NLPSearchEngine;

CREATE TABLE NLPSearchEngine.dbo.DocumentCategory (
	Id INT IDENTITY PRIMARY KEY,
	Name NVARCHAR(32),
);

CREATE TABLE NLPSearchEngine.dbo.DocumentSource (
	Id INT IDENTITY PRIMARY KEY,
	Name NVARCHAR(32),
);

CREATE TABLE NLPSearchEngine.dbo.Document (
	Id BIGINT IDENTITY PRIMARY KEY,
	Title NVARCHAR(200),
	CategoryId INT,
	SourceId INT,
	Body NVARCHAR(MAX),
	FOREIGN KEY (CategoryId) REFERENCES NLPSearchEngine.dbo.DocumentCategory(Id),
	FOREIGN KEY (SourceId) REFERENCES NLPSearchEngine.dbo.DocumentSource(Id),
);

DROP TABLE NLPSearchEngine.dbo.Document
DROP TABLE NLPSearchEngine.dbo.DocumentSource
DROP TABLE NLPSearchEngine.dbo.DocumentCategory
