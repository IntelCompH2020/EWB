from flask_restx import Namespace, Resource, fields, reqparse
from core.client.solr_client import SolrClient

# ======================================================
# Define namespace for managing models
# ======================================================
api = Namespace('Models', description='Models related operations')

# ======================================================
# Collection metadata for doc and response marshalling
# ======================================================
# corpus = api.model('Corpus', {
#     'name': fields.String(required=True,
#                           description='The corpus name'),
#     'ndocs': fields.String(required=True,
#                            description='The number of documents in the corpus')
# })

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = SolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument(
    'corpus_name', help='Specify the name of the corpus to index')
parser.add_argument('collection', help='Specify collection name')
parser.add_argument(
    'model_name', help='Specify the name of the corpus to index')


@api.route('/indexModel/')
class IndexModel(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        model_name = args['model_name']
        collection = args['collection']
        sc.update_info_model(model_name, collection)
        return '', 200
