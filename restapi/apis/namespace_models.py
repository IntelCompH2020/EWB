"""
This script defines a Flask RESTful namespace for managing models stored in Solr as collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/04/2023
"""
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
# parser.add_argument(
#     'collection_name', help='Specify name of the collection where the model will be indexed')
parser.add_argument(
    'model_name', help='Specify the name of the model to index')


@api.route('/indexModel/')
class IndexModel(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        #collection_name = args['collection_name']
        model_name = args['model_name']
        sc.index_model(model_name)
        return '', 200
