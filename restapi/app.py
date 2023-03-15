from flask import Flask
from flask_restx import Api, Resource, reqparse

from client.solr_client import SolrClient

# Create Flask app
app = Flask(__name__)
api = Api(app, version='1.0', title='Evaluation Workbench API')

parser = reqparse.RequestParser()
parser.add_argument('collection', help='Specify collection name')

# Create Solr client
sc = SolrClient(app.logger)


@api.route('/createCollection/')
class CreateCollection(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        collection = args['collection']
        sc.create_collection(col_name=collection)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
