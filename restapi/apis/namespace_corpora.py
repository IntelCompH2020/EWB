"""
This script defines a Flask RESTful namespace for managing corpora stored in Solr as collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""
from flask_restx import Namespace, Resource, fields, reqparse
from core.client.ewb_solr_client import EWBSolrClient

# ======================================================
# Define namespace for managing corpora
# ======================================================
api = Namespace('Corpora', description='Corpora-related operations')

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
sc = EWBSolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument(
    'corpus_path', help="Specify the path of the corpus to index / delete (i.e., path to the json file within the /datasets folder in the project folder describing a ITMT's logical corpus)")


@api.route('/indexCorpus/')
class IndexCorpus(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        corpus_path = args['corpus_path']
        sc.index_corpus(corpus_path)
        return '', 200


@api.route('/deleteCorpus/')
class DeleteCorpus(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        corpus_path = args['corpus_path']
        sc.delete_corpus(corpus_path)
        return '', 200
