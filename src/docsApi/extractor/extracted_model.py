class ExtractedModel:
    def __init__(self, tfidf_fit_content, tfidf_transform_title, tfidf_transform_body, tfidf_fit_lsa, lsa_fit,
                 lsa_transform, document_category_semantic_vector_index, category_semantic_vectors):
        self.tfidf_fit_content = tfidf_fit_content
        self.tfidf_transform_title = tfidf_transform_title
        self.tfidf_transform_body = tfidf_transform_body
        self.tfidf_fit_lsa = tfidf_fit_lsa
        self.lsa_fit = lsa_fit
        self.lsa_transform = lsa_transform
        self.document_category_semantic_vector_index = document_category_semantic_vector_index
        self.category_semantic_vectors = category_semantic_vectors
