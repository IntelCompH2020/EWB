"""
This script defines a Flask RESTful namespace for managing corpora stored in Solr as collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/04/2023
"""
from flask_restx import Namespace, Resource, fields, reqparse
from core.client.solr_client import SolrClient

# ======================================================
# Define namespace for managing corpora
# ======================================================
api = Namespace('Corpora', description='Corpora related operations')

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


@api.route('/indexCorpus/')
class IndexCorpus(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        corpus_name = args['corpus_name']
        collection = args['collection']
        sc.index_corpus(corpus_name)#collection
        return '', 200
