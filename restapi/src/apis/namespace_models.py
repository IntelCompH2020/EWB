"""
This script defines a Flask RESTful namespace for managing models stored in Solr as collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

from flask_restx import Namespace, Resource, reqparse
from src.core.clients.ewb_solr_client import EWBSolrClient

# ======================================================
# Define namespace for managing models
# ======================================================
api = Namespace(
    'Models', description='Models-related operations for the EWB (i.e., index/delete models))')

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument(
    'model_path', help="Specify the path of the model to index / delete (i.e., path to the folder within the TMmodels folder in the project folder describing a ITMT's topic model)")


@api.route('/indexModel/')
class IndexModel(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        model_path = args['model_path']
        sc.index_model(model_path)
        return '', 200


@api.route('/deleteModel/')
class DeleteModel(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        model_path = args['model_path']
        sc.delete_model(model_path)
        return '', 200


@api.route('/listAllModels/')
class ListAllModels(Resource):
    def get(self):
        models_lst, code = sc.list_model_collections()
        return models_lst, code
