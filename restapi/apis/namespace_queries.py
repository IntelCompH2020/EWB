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
api = Namespace(
    'Queries', description='Specfic Solr queries for the EWB.')

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

q3_parser = reqparse.RequestParser()
q3_parser.add_argument(
    'collection', help='Name of the collection', required=True)

q4_parser = reqparse.RequestParser()
q4_parser.add_argument(
    'corpus_collection', help='Name of the corpus collection', required=True)
q4_parser.add_argument(
    'model_name', help='Name of the model reponsible for the creation of the doc-topic distribution', required=True)
q4_parser.add_argument(
    'topic_id', help='Topic whose proportion must be larger than a certain threshold', required=True)
q4_parser.add_argument(
    'threshold', help='Query threshold', required=True)
q4_parser.add_argument(
    'start', help='Specifies an offset (by default, 0) into the responses at which Solr should begin displaying content.', required=False)
q4_parser.add_argument(
    'rows', help='Controls how many rows of responses are displayed at a time (default value: maximum number of docs in the collection)', required=False)

q5_parser = reqparse.RequestParser()
q5_parser.add_argument(
    'corpus_collection', help='Name of the corpus collection', required=True)
q5_parser.add_argument(
    'model_name', help='Name of the model reponsible for the creation of the doc-topic distribution', required=True)
q5_parser.add_argument(
    'doc_id', help="ID of the document whose similarity is going to be checked against all other documents in 'corpus_collection'", required=True)
q5_parser.add_argument(
    'start', help='Specifies an offset (by default, 0) into the responses at which Solr should begin displaying content', required=False)
q5_parser.add_argument(
    'rows', help='Controls how many rows of responses are displayed at a time (default value: maximum number of docs in the collection)', required=False)


@api.route('/getThetasDocById/')
class get_thetas_doc_by_id(Resource):
    @api.doc(parser=q1_parser)
    def get(self):
        args = q1_parser.parse_args()
        corpus_collection = args['corpus_collection']
        doc_id = args['doc_id']
        model_name = args['model_name']

        return sc.do_Q1(corpus_col=corpus_collection,
                        doc_id=doc_id,
                        model_name=model_name)


@api.route('/getNrDocsColl/')
class get_nr_docs_coll(Resource):
    @api.doc(parser=q3_parser)
    def get(self):
        args = q3_parser.parse_args()
        collection = args['collection']

        return sc.do_Q3(col=collection)


@api.route('/getDocsWithThetasLargerThanThr/')
class get_docs_with_thetas_larger_than_thr(Resource):
    @api.doc(parser=q4_parser)
    def get(self):
        args = q4_parser.parse_args()
        corpus_collection = args['corpus_collection']
        model_name = args['model_name']
        topic_id = args['topic_id']
        threshold = args['threshold']
        start = args['start']
        rows = args['rows']

        return sc.do_Q4(corpus_col=corpus_collection,
                        model_name=model_name,
                        topic_id=topic_id,
                        thr=threshold,
                        start=start,
                        rows=rows)


@api.route('/getDocsWithHighSemanticRelationshipWithDocid/')
class get_docs_with_high_semantic_relationship_with_docid(Resource):
    @api.doc(parser=q5_parser)
    def get(self):
        args = q5_parser.parse_args()
        corpus_collection = args['corpus_collection']
        model_name = args['model_name']
        doc_id = args['doc_id']
        start = args['start']
        rows = args['rows']

        return sc.do_Q5(corpus_col=corpus_collection,
                        model_name=model_name,
                        doc_id=doc_id,
                        start=start,
                        rows=rows)
