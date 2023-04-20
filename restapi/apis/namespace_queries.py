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
api = Namespace('Queries', description='Specfic Solr queries for the EWB (i.e., Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, etc.)')

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parsers to take inputs from user
q1_parser = reqparse.RequestParser()
q1_parser.add_argument(
    'corpus_collection', help='Name of the corpus collection', required=True)
q1_parser.add_argument(
    'doc_id', help='ID of the document whose whose doc-topic distribution associated to a specific model is to be retrieved', required=True)
q1_parser.add_argument(
    'model_name', help='Name of the model reponsible for the creation of the doc-topic distribution to be retrieved', required=True)
q1_parser.add_argument(
    'results_file_path', help="Path to the file where the results will be stored. If not specified, it will be saved in '/data/results/{corpus_collection}\_Q1\_{date}.json'", required=False)

q2_parser = reqparse.RequestParser()
q2_parser.add_argument(
    'collection', help='Name of the collection', required=True)
q2_parser.add_argument(
    'results_file_path', help="Path to the file where the results will be stored. If not specified, it will be saved in '/data/results/{collection}\_Q2\_{date}.json'", required=False)

q3_parser = reqparse.RequestParser()
q3_parser.add_argument(
    'corpus_collection', help='Name of the corpus collection', required=True)
q3_parser.add_argument(
    'model_name', help='Name of the model reponsible for the creation of the doc-topic distribution', required=True)
q3_parser.add_argument(
    'topic_id', help='Topic whose proportion must be larger than a certain threshold', required=True)
q3_parser.add_argument(
    'threshold', help='Query threshold', required=True)
q3_parser.add_argument(
    'results_file_path', help="Path to the file where the results will be stored. If not specified, it will be saved in '/data/results/{corpus_collection}\_Q3\_{date}.json'", required=False)


@api.route('/q1/')
class Q1(Resource):
    @api.doc(parser=q1_parser)
    def get(self):
        args = q1_parser.parse_args()
        corpus_collection = args['corpus_collection']
        doc_id = args['doc_id']
        model_name = args['model_name']
        results_file_path = args['results_file_path']

        if results_file_path is None:
            results_file_path = f"/data/results/{corpus_collection}_Q1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        status_code = sc.do_Q1(corpus_col=corpus_collection, doc_id=doc_id,
                               model_name=model_name, results_file_path=results_file_path)

        return '', status_code


@api.route('/q2/')
class Q2(Resource):
    @api.doc(parser=q2_parser)
    def get(self):
        args = q2_parser.parse_args()
        collection = args['collection']
        results_file_path = args['results_file_path']

        if results_file_path is None:
            results_file_path = f"/data/results/{collection}_Q2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        _, status_code = sc.do_Q2(col=collection,
                                  results_file_path=results_file_path)

        return '', status_code


@api.route('/q3/')
class Q3(Resource):
    @api.doc(parser=q3_parser)
    def get(self):
        args = q3_parser.parse_args()
        corpus_collection = args['corpus_collection']
        model_name = args['model_name']
        topic_id = args['topic_id']
        threshold = args['threshold']
        results_file_path = args['results_file_path']

        if results_file_path is None:
            results_file_path = f"/data/results/{corpus_collection}_Q3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        status_code = sc.do_Q3(corpus_col=corpus_collection, model_name=model_name,
                               topic_id=topic_id, thr=threshold, results_file_path=results_file_path)

        return '', status_code
