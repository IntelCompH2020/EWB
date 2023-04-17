"""
This script defines a Flask RESTful namespace for managing Solr queries.

Author: Lorena Calvo-Bartolomé
Date: 13/04/2023
"""

from flask_restx import Namespace, Resource, reqparse
from core.client.ewb_solr_client import EWBSolrClient

# ======================================================
# Define namespace for managing queries
# ======================================================
api = Namespace('Queries', description='Solr queries')

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument(
    'model_name', help='Specify the name of the model to index')


# Q1: 
@api.route('/q1/')
class Q1(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        model_name = args['model_name']
        sc.index_model(model_name)
        return '', 200
    
# @TODO: Implement here the rest of the queries