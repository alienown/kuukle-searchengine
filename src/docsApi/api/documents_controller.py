from flask import request, Response
from flask_restful import Resource, marshal_with
from document_service import DocumentService
from response_model import fields as response_fields
from distutils.util import strtobool

class DocumentsController(Resource):
    def __init__(self):
        self.document_service = DocumentService()

    @marshal_with(response_fields)
    def get(self):
        query = request.args.get('query', default='')
        page = int(request.args.get('pageNumber', default=1))
        force_query = bool(strtobool(request.args.get('forceQuery', default='false')))
        try:
            result = self.document_service.get_documents(query, page, force_query)
            return result, 200
        except BaseException as e:
            print(e)
            return Response(status=500)
