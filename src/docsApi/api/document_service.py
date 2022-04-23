import sys
import os
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import dill
import pandas as pd
from document_model import DocumentModel
from response_model import ResponseModel
import spacy
import pkg_resources
from symspellpy import SymSpell, Verbosity

sys.path.append(os.path.abspath(os.path.join('..', 'extractor')))

sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
dictionary_path = os.path.join(os.path.abspath(os.path.join('..', 'extractor')), 'suggestion_vocab.txt')
bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")
sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

model = dill.load(open(os.path.abspath(os.path.join(os.path.join('..', 'extractor'), 'extracted_model')), 'rb'))
nlp = spacy.load("en_core_web_sm")
page_size = 10

class DocumentService:
    def clean_text(self, text):
        result = []
        splitted = text.split()
        for token in splitted:
            if len(token) == 1 and (token.isalpha() or token.isnumeric()):
                result.append(token)
            else:
                tokenized_tokens = re.findall('\w+.*\w+', token)
                result = result + tokenized_tokens
        return ' '.join(result)

    def prepare_text(self, text, remove_stopwords=True, lemmatize=True, min_word_count=2):
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

    def create_query_vector(self, prepared_query):
        query_terms_to_topics = []
        query_vector = []
        terms_to_topics = model.lsa_fit.components_.transpose()
        for word in prepared_query.split():
            index = model.tfidf_fit_lsa.vocabulary_.get(word)
            if index is not None:
                query_terms_to_topics.append(terms_to_topics[index].tolist())
        if len(query_terms_to_topics) > 0:
            query_vector = np.sum(np.array(query_terms_to_topics), axis=0).tolist()
        return np.array(query_vector)

    def create_scores_dataframe(self, title_similarities=[], body_similarities=[], semantic_similarities=[], scores=[]):
        dataframe = pd.DataFrame(data={
            'Title score': title_similarities,
            'Body score': body_similarities,
            'Semantic score': semantic_similarities,
            'Score': scores
        })

        return dataframe

    def get_scored_documents(self, query):
        cleaned_query = self.clean_text(query)
        lemmatized_query = self.prepare_text(cleaned_query, remove_stopwords=False, min_word_count=0)
        tfidf_query = cleaned_query + ' ' + lemmatized_query
        semantic_query = self.prepare_text(cleaned_query)

        tfidf_query_vector = model.tfidf_fit_content.transform([tfidf_query])
        semantic_query_vector = self.create_query_vector(semantic_query)

        is_tfidf_query_vector_empty = tfidf_query_vector.nnz == 0
        is_semantic_query_vector_empty = not semantic_query_vector.any()

        if is_tfidf_query_vector_empty and is_semantic_query_vector_empty:
            return self.create_scores_dataframe()

        reshaped_semantic_query_vector = semantic_query_vector.reshape(1, -1)
        semantic_similarities = cosine_similarity(reshaped_semantic_query_vector, model.lsa_transform)
        query_category_semantic_similarities = cosine_similarity(reshaped_semantic_query_vector,
                                                                 np.array(model.category_semantic_vectors))
        normalized_semantic_similarities = []

        title_similarities = cosine_similarity(tfidf_query_vector, model.tfidf_transform_title)
        body_similarities = cosine_similarity(tfidf_query_vector, model.tfidf_transform_body)

        overall_scores = []
        for index in range(len(model.lsa_transform)):
            semantic_similarity = (semantic_similarities[0][index] + query_category_semantic_similarities[0][
                model.document_category_semantic_vector_index[index]]) / 2
            normalized_semantic_similarities.append(semantic_similarity)

            score = (body_similarities[0][index] * semantic_similarity +
                     title_similarities[0][index] +
                     semantic_similarity) / 3

            overall_scores.append(score)

        dataframe = self.create_scores_dataframe(title_similarities[0],
                                                 body_similarities[0],
                                                 normalized_semantic_similarities,
                                                 overall_scores)

        dataframe = dataframe.sort_values(by=['Score'], ascending=False)

        return dataframe

    def get_document_models(self, scored_documents_dataframe):
        models = []

        for index, document in scored_documents_dataframe.iterrows():
            model = DocumentModel(id=index + 1,
                                  title_score=document['Title score'],
                                  body_score=document['Body score'],
                                  semantic_score=document['Semantic score'],
                                  score=document['Score'])
            models.append(model)

        return models

    def get_suggested_query(self, query):
        suggestions = sym_spell.lookup_compound(query, max_edit_distance=3, transfer_casing=True)
        terms = [suggestion.term for suggestion in suggestions if suggestion.distance > 0]
        if len(terms) > 0:
            return terms[0]
        return None

    def get_documents(self, query, page, force_query):
        suggested_query = self.get_suggested_query(query)
        if suggested_query is not None and not force_query:
            query = suggested_query
        elif force_query:
            suggested_query = None
        scored_documents_dataframe = self.get_scored_documents(query)
        scored_documents_dataframe = scored_documents_dataframe[scored_documents_dataframe['Score'] > 0.1]
        total = len(scored_documents_dataframe.index)
        offset = page_size * (page - 1)
        documents = self.get_document_models(scored_documents_dataframe[offset:offset + page_size])
        result = ResponseModel(documents, total, suggested_query)
        return result
