from flask import Flask
from flask_restful import Api
from documents_controller import DocumentsController

app = Flask(__name__)
api = Api(app)

api.add_resource(DocumentsController, '/documents')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
