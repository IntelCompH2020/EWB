"""
This script defines a Flask RESTful namespace for managing Solr queries.

Author: Lorena Calvo-Bartolomé
Date: 13/04/2023
"""

from datetime import datetime
from flask_restx import Namespace, Resource, reqparse
from core.client.ewb_solr_client import EWBSolrClient

# ======================================================
# Define namespace for managing queries
# ======================================================
api = Namespace('Queries', description='Specfic Solr queries for the EWB')

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parser to take inputs from user
q1_parser = reqparse.RequestParser()
q1_parser.add_argument(
    'corpus_collection', help='Name of the corpus collection', required=True)
q1_parser.add_argument(
    'doc_id', help='ID of the document whose whose doc-topic distribution associated to a specific model is to be retrieved', required=True)
q1_parser.add_argument(
    'model_name', help='Name of the model reponsible for the creation of the doc-topic distribution to be retrieved', required=True)
q1_parser.add_argument(
    'results_file_path', help="Path to the file where the results will be stored. If not specified, it will be saved in '/data/results/{corpus_collection}\_Q1\_{date}.json'", required=False)

# Q1: Retrieve document-topic distribution of document in a corpus collection


@api.route('/q1/')
class Q1(Resource):
    @api.doc(parser=q1_parser,
             doc="Retrieve document-topic distribution of document in a corpus collection")
    def post(self):
        args = q1_parser.parse_args()
        corpus_collection = args['corpus_collection']
        doc_id = args['doc_id']
        model_name = args['model_name']
        results_file_path = args['results_file_path']

        if results_file_path is None:
            results_file_path = f"/data/results/{corpus_collection}_Q1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        sc.do_Q1(corpus_col=corpus_collection, doc_id=doc_id,
                 model_name=model_name, results_file_path=results_file_path)

        return '', 200
