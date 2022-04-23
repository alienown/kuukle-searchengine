from flask_restful import fields
from document_model import fields as document_fields

class ResponseModel:
    def __init__(self, documents, total, suggested_query):
        self.documents = documents
        self.total = total
        self.suggestedQuery = suggested_query

fields = {
    'documents': fields.List(fields.Nested(document_fields)),
    'total': fields.Integer,
    'suggestedQuery': fields.String
}
