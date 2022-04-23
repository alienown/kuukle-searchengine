from flask_restful import fields

class DocumentModel:
    def __init__(self, id, title_score, body_score, semantic_score, score):
        self.id = id
        self.titleScore = title_score
        self.bodyScore = body_score
        self.semanticScore = semantic_score
        self.score = score

fields = {
    'id': fields.Integer,
    'titleScore': fields.Float,
    'bodyScore': fields.Float,
    'semanticScore': fields.Float,
    'score': fields.Float
}
