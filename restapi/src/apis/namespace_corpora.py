"""
This script defines a Flask RESTful namespace for managing corpora stored in Solr as collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""
from flask_restx import Namespace, Resource, fields, reqparse
from src.core.clients.ewb_solr_client import EWBSolrClient

# ======================================================
# Define namespace for managing corpora
# ======================================================
api = Namespace(
    'Corpora', description='Corpora-related operations for the EWB (i.e., index/delete corpora))')

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument(
    'corpus_path', help="Path of the corpus to index / delete (i.e., path to the json file within the /datasets folder in the project folder describing a ITMT's logical corpus)")

parser2 = reqparse.RequestParser()
parser2.add_argument(
    'corpus_col', help="Name of the corpus collection to list its models")


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


@api.route('/listAllCorpus/')
class listAllCorpus(Resource):
    def get(self):
        corpus_lst, code = sc.list_corpus_collections()
        return corpus_lst, code


@api.route('/listCorpusModels/')
class listCorpusModels(Resource):
    @api.doc(parser=parser2)
    def get(self):
        args = parser2.parse_args()
        corpus_col = args['corpus_col']
        corpus_lst, code = sc.get_corpus_models(corpus_col=corpus_col)
        return corpus_lst, code
