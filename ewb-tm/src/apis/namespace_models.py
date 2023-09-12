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
    'Models', description='Models-related operations (i.e., index/delete models))')

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
        try:
            sc.index_model(model_path)
            return '', 200
        except Exception as e:
            return str(e), 500


@api.route('/deleteModel/')
class DeleteModel(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        model_path = args['model_path']
        try:
            sc.delete_model(model_path)
            return '', 200
        except Exception as e:
            return str(e), 500

@api.route('/listAllModels/')
class ListAllModels(Resource):
    def get(self):
        try:
            models_lst, code = sc.list_model_collections()
            return models_lst, code
        except Exception as e:
            return str(e), 500
