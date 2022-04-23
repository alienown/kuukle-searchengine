import sys
import json
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
import numpy as np
import pandas as pd
import re
import os
import pyodbc
import dill
from extracted_model import ExtractedModel

import spacy
nlp = spacy.load("en_core_web_sm")

class Config:
    def __init__(self, config):
        self.bbc_path = config['bbcPath']
        self.db_connection_string = config['dbConnectionString']

def clean_text(text):
    lowercased_text = text.lower()
    result = []
    splitted = lowercased_text.split()
    for token in splitted:
        if len(token) == 1 and (token.isalpha() or token.isnumeric()):
            result.append(token)
        else:
            tokenized_tokens = re.findall('\w+.*\w+', token)
            result = result + tokenized_tokens
    return ' '.join(result)


def prepare_text(text, remove_stopwords=True, lemmatize=True, min_word_count=2):
    exclude_words = ['\'re', 'n\'t', '\'ve', 'em', '\'ll']
    tokenized_text = nlp(text)

    filtered_tokenized_text = [token for token in tokenized_text
                               if (not token.is_stop or not remove_stopwords) and
                               token.text.lower() not in exclude_words and
                               re.search('\w*[a-zA-Z]\w*', token.text) and
                               len(token.text) > min_word_count]

    if lemmatize:
        filtered_tokenized_text = [token.lemma_ for token in filtered_tokenized_text]
    else:
        filtered_tokenized_text = [token.text for token in filtered_tokenized_text]

    return ' '.join(filtered_tokenized_text)


def prepare_newsgroup_documents(corpus):
    print('Preparing newsgroups documents...')

    titles = []
    titles_cleaned = []
    titles_lemmatized = []
    titles_lemmatized_no_stopwords = []
    bodies = []
    bodies_cleaned = []
    bodies_lemmatized = []
    bodies_lemmatized_no_stopwords = []
    categories = []
    for index, body in enumerate(corpus.data):
        titleIndex = body.find('Subject:')
        endLineAfterTitleIndex = body.find('\n', titleIndex)
        linesIndex = body.find('Lines:')
        headerIndex = body.find('\n', linesIndex)

        if headerIndex > 0 and linesIndex > 0 and endLineAfterTitleIndex > 0 and titleIndex > 0:
            body_without_header = body[headerIndex:]
            body_title = body[titleIndex:endLineAfterTitleIndex + 1]

            extracted_title = body_title[8:len(body_title) - 1].strip()
            title_cleaned = re.sub('(?i)re:', ' ', extracted_title)
            title_cleaned = re.sub(
                '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
                ' ', title_cleaned)
            title_cleaned = re.sub(
                '(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])*',
                ' ', title_cleaned)
            title_cleaned = re.sub('\n', ' ', title_cleaned)

            title_cleaned = clean_text(title_cleaned);
            title_lemmatized = prepare_text(title_cleaned, remove_stopwords=False, min_word_count=0)
            title_lemmatized_no_stopwords = prepare_text(title_cleaned)

            body_cleaned = re.sub('(?i)re:', ' ', body_without_header)
            body_cleaned = re.sub('(From article.*by.*\n)|(From.*\n)', ' ', body_cleaned)
            body_cleaned = re.sub('(In article <.*>.*\n)|(.*writes:\n)|(.*wrote:\n)', ' ', body_cleaned)
            body_cleaned = re.sub(
                '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
                ' ', body_cleaned)
            body_cleaned = re.sub(
                '(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])*',
                ' ', body_cleaned)
            body_cleaned = re.sub('\n', ' ', body_cleaned)
            body_cleaned = clean_text(body_cleaned)
            body_lemmatized = prepare_text(body_cleaned, remove_stopwords=False, min_word_count=0)
            body_lemmatized_no_stopwords = prepare_text(body_cleaned)

            titles_cleaned.append(title_cleaned)
            titles_lemmatized.append(title_lemmatized)
            titles_lemmatized_no_stopwords.append(title_lemmatized_no_stopwords)
            titles.append(extracted_title)

            bodies_cleaned.append(body_cleaned)
            bodies_lemmatized.append(body_lemmatized)
            bodies_lemmatized_no_stopwords.append(body_lemmatized_no_stopwords)
            bodies.append(body)

            category_index = corpus.target[index]
            categories.append(corpus.target_names[category_index])

    df = pd.DataFrame()
    df['Title'] = titles
    df['Cleaned title'] = titles_cleaned
    df['Cleaned title lemmatized'] = titles_lemmatized
    df['Cleaned title lemmatized no stopwords'] = titles_lemmatized_no_stopwords
    df['Body'] = bodies
    df['Cleaned body'] = bodies_cleaned
    df['Cleaned body lemmatized'] = bodies_lemmatized
    df['Cleaned body lemmatized no stopwords'] = bodies_lemmatized_no_stopwords
    df['Category'] = categories
    df['Source'] = '20newsgroup'

    return df


class BBCDirectory:
    def __init__(self, parent_path, business_path, entertainment_path, politics_path, sport_path, tech_path):
        self.parent_path = parent_path
        self.business_path = business_path
        self.entertainment_path = entertainment_path
        self.politics_path = politics_path
        self.sport_path = sport_path
        self.tech_path = tech_path


def get_bbc_original_directory(bbc_path):
    if bbc_path:
        bbc_root_path = bbc_path
    else:
        bbc_root_path = os.path.join('.', 'bbc')

    bbc_business_path = os.path.join(bbc_root_path, 'business')
    bbc_entertainment_path = os.path.join(bbc_root_path, 'entertainment')
    bbc_politics_path = os.path.join(bbc_root_path, 'politics')
    bbc_sport_path = os.path.join(bbc_root_path, 'sport')
    bbc_tech_path = os.path.join(bbc_root_path, 'tech')

    if not os.path.exists(bbc_business_path) or \
        not os.path.exists(bbc_entertainment_path) or \
        not os.path.exists(bbc_politics_path) or \
        not os.path.exists(bbc_sport_path) or \
        not os.path.exists(bbc_tech_path):
        raise Exception('BBC directory is not valid')

    directory = BBCDirectory(bbc_root_path, bbc_business_path, bbc_entertainment_path,
                             bbc_politics_path, bbc_sport_path, bbc_tech_path)

    return directory


def load_documents_from_directory(directory_path):
    documents = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            path = os.path.join(directory_path, filename)
            file = open(path, 'r')
            content = file.read()
            documents.append(content)
            file.close()
    return documents


def load_bbc_documents(config):
    print('Loading bbc documents from directory...')

    original_directory = get_bbc_original_directory(config.bbc_path)

    business_documents = load_documents_from_directory(original_directory.business_path)
    entertainment_documents = load_documents_from_directory(original_directory.entertainment_path)
    politics_documents = load_documents_from_directory(original_directory.politics_path)
    sport_documents = load_documents_from_directory(original_directory.sport_path)
    tech_documents = load_documents_from_directory(original_directory.tech_path)

    return {
        'business': business_documents,
        'entertainment': entertainment_documents,
        'politics': politics_documents,
        'sport': sport_documents,
        'tech': tech_documents
    }


def prepare_bbc_documents(bbc_data):
    print('Preparing bbc documents...')

    titles = []
    titles_cleaned = []
    titles_lemmatized = []
    titles_lemmatized_no_stopwords = []
    bodies = []
    bodies_cleaned = []
    bodies_lemmatized = []
    bodies_lemmatized_no_stopwords = []
    categories = []
    for bbc_category in bbc_data:
        bbc_articles = bbc_data[bbc_category]
        for body in bbc_articles:
            splitted_text = [paragraph for paragraph in body.split('\n') if paragraph != '']
            extracted_title = splitted_text[0]
            extracted_body = '\n'.join(splitted_text[1:])

            title_cleaned = re.sub(
                '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
                '', extracted_title)
            title_cleaned = re.sub(
                '(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])*',
                '', title_cleaned)
            title_cleaned = re.sub('\n', ' ', title_cleaned)
            title_cleaned = clean_text(title_cleaned)
            title_lemmatized = prepare_text(title_cleaned, remove_stopwords=False, min_word_count=0)
            title_lemmatized_no_stopwords = prepare_text(title_cleaned)

            body_cleaned = re.sub(
                '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
                '', extracted_body)
            body_cleaned = re.sub(
                '(?:[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])*',
                '', body_cleaned)
            body_cleaned = re.sub('\n', ' ', body_cleaned)
            body_cleaned = clean_text(body_cleaned)
            body_lemmatized = prepare_text(body_cleaned, remove_stopwords=False, min_word_count=0)
            body_lemmatized_no_stopwords = prepare_text(body_cleaned)

            titles.append(extracted_title)
            titles_cleaned.append(title_cleaned)
            titles_lemmatized.append(title_lemmatized)
            titles_lemmatized_no_stopwords.append(title_lemmatized_no_stopwords)
            bodies_cleaned.append(body_cleaned)
            bodies_lemmatized.append(body_lemmatized)
            bodies_lemmatized_no_stopwords.append(body_lemmatized_no_stopwords)
            bodies.append(extracted_body)
            categories.append(bbc_category)

    df = pd.DataFrame()
    df['Title'] = titles
    df['Cleaned title'] = titles_cleaned
    df['Cleaned title lemmatized'] = titles_lemmatized
    df['Cleaned title lemmatized no stopwords'] = titles_lemmatized_no_stopwords
    df['Body'] = bodies
    df['Cleaned body'] = bodies_cleaned
    df['Cleaned body lemmatized'] = bodies_lemmatized
    df['Cleaned body lemmatized no stopwords'] = bodies_lemmatized_no_stopwords
    df['Category'] = categories
    df['Source'] = 'bbc'

    return df


def tfidf_tokenizer(text):
    return text.split()


def calculate_category_vector(category_documents, lsa_fit_transform):
    articles_vectors = []
    for index, article in category_documents.iterrows():
        articles_vectors.append(lsa_fit_transform[index])
    return np.mean(articles_vectors, axis=0)


def get_category_semantic_vectors(documents_df, lsa_fit_transform):
    grouped = documents_df.groupby(['Category'])
    category_vectors_dict = {}
    for category, group in grouped:
        category_vector = calculate_category_vector(group, lsa_fit_transform)
        category_vectors_dict[category] = category_vector
    category_vectors_dict = dict(sorted(category_vectors_dict.items()))
    return category_vectors_dict


def get_document_category_semantic_vector_index_array(documents_df, category_semantic_vectors_dict):
    document_category_semantic_vector_index = []
    categories = list(category_semantic_vectors_dict.keys())
    document_categories = documents_df['Category'].values
    for category in document_categories:
        document_category_semantic_vector_index.append(categories.index(category))
    return document_category_semantic_vector_index

def load_20newsgroups_documents():
    print('Loading 20newsgroups documents...')
    newsgroups_train = fetch_20newsgroups(subset='train')
    return newsgroups_train

def get_documents(config):
    bbc_data = load_bbc_documents(config)
    bbc_df = prepare_bbc_documents(bbc_data)
    
    newsgroups_train = load_20newsgroups_documents()
    newsgroup_df = prepare_newsgroup_documents(newsgroups_train)
    
    documents_df = bbc_df.append(newsgroup_df, ignore_index=True)
    
    return documents_df


def create_db_connection(config):
    db_connection = pyodbc.connect(config.db_connection_string)

    return db_connection


def insert_documents_to_database(config, documents_df):
    print('Inserting documents to database...')

    db_connection = create_db_connection(config)
    cursor = db_connection.cursor()
    db_connection.autocommit = False

    db_connection.commit()
    categories = list(documents_df['Category'].unique())
    categories.sort()
    sources = list(documents_df['Source'].unique())
    sources.sort()

    categories_to_ids = {}
    sources_to_ids = {}

    try:
        for category in categories:
            cursor.execute('INSERT INTO [dbo].[DocumentCategory] (Name) VALUES (?)', category)
            category_id = cursor.execute('SELECT @@IDENTITY').fetchone()[0]
            categories_to_ids[category] = category_id

        for source in sources:
            cursor.execute('INSERT INTO [dbo].[DocumentSource] (Name) VALUES (?)', source)
            source_id = cursor.execute('SELECT @@IDENTITY').fetchone()[0]
            sources_to_ids[source] = source_id

        for index, document in documents_df.iterrows():
            cursor.execute('INSERT INTO [dbo].[Document] (Title, CategoryId, SourceId, Body) VALUES (?, ?, ?, ?)',
                           document['Title'], categories_to_ids[document['Category']],
                           sources_to_ids[document['Source']], document['Body'])

        db_connection.commit()
    except BaseException as err:
        db_connection.rollback()
        raise err
    finally:
        db_connection.autocommit = True


def create_suggestion_vocab(documents_df):
    count_vectorizer = CountVectorizer()
    count_vectorizer_transform = count_vectorizer.fit(documents_df['Cleaned title'] + ' ' +
                                                      documents_df['Cleaned title lemmatized'] + ' ' +
                                                      documents_df['Cleaned body'] + ' ' +
                                                      documents_df['Cleaned body lemmatized'])
    f = open("suggestion_vocab.txt", "w")
    for key in count_vectorizer_transform.vocabulary_:
        try:
            string = str(key) + ' ' + str(count_vectorizer_transform.vocabulary_[key]) + '\n'
            f.write(string)
        except UnicodeEncodeError:
            continue
    f.close()

def get_config():
    f = open('config.json')
    config = Config(json.load(f))
    return config

if __name__ == '__main__':
    config = get_config()

    documents_df = get_documents(config)
    insert_documents_to_database(config, documents_df)

    print('Creating model...')
    
    tfidf_vectorizer_lsa = TfidfVectorizer(tokenizer=tfidf_tokenizer, lowercase=False)
    tfidf_fit_lsa = tfidf_vectorizer_lsa.fit(documents_df['Cleaned title lemmatized no stopwords'] + ' ' + documents_df['Cleaned body lemmatized no stopwords'])
    tfidf_transform_lsa = tfidf_fit_lsa.fit_transform(documents_df['Cleaned title lemmatized no stopwords'] + ' ' + documents_df['Cleaned body lemmatized no stopwords'])

    tfidf_vectorizer_content = TfidfVectorizer(tokenizer=tfidf_tokenizer, lowercase=False)
    tfidf_fit_content = tfidf_vectorizer_content.fit(documents_df['Cleaned title'] + ' ' + documents_df['Cleaned title lemmatized'] + ' ' + documents_df['Cleaned body'] + ' ' + documents_df['Cleaned body lemmatized'])
    tfidf_transform_title = tfidf_fit_content.transform(documents_df['Cleaned title'] + ' ' + documents_df['Cleaned title lemmatized'])
    tfidf_transform_body = tfidf_fit_content.transform(documents_df['Cleaned body'] + ' ' + documents_df['Cleaned body lemmatized'])

    svd = TruncatedSVD(n_components=25, random_state=42)
    lsa_fit = svd.fit(tfidf_transform_lsa)
    lsa_transform = lsa_fit.transform(tfidf_transform_lsa)
    category_semantic_vectors_dict = get_category_semantic_vectors(documents_df, lsa_transform)
    document_category_semantic_vector_index = get_document_category_semantic_vector_index_array(documents_df, category_semantic_vectors_dict)

    create_suggestion_vocab(documents_df)

    extracted_model = ExtractedModel(tfidf_fit_content, tfidf_transform_title, tfidf_transform_body, tfidf_fit_lsa, lsa_fit, lsa_transform,
                                     document_category_semantic_vector_index, list(category_semantic_vectors_dict.values()))
    dill.dump(extracted_model, open("extracted_model", "wb"))
