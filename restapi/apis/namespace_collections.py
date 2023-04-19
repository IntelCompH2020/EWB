"""
This script defines a Flask RESTful namespace for managing Solr collections. 

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

from datetime import datetime
import json

from core.client.ewb_solr_client import EWBSolrClient
from flask_restx import Namespace, Resource, fields, reqparse

# ======================================================
# Define namespace for managing collections
# ======================================================
api = Namespace('Collections',
                description='Generic Solr-related operations (collections creation and deletion, queries, etc.)')

# ======================================================
# Collection metadata for doc and response marshalling
# ======================================================
coll = api.model('Collection', {
    'name': fields.String(required=True,
                          description='The collection name')
})

# ======================================================
# Namespace variables
# ======================================================
# Create Solr client
sc = EWBSolrClient(api.logger)

# Define parsers to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument('collection', help='Collection name')

query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'collection', help='Collection name on which you want to execute the query. This parameter is mandatory', required=True)
query_parser.add_argument(
    'results_file_path', help="Path to the file where the results will be stored. If not specified, it will be saved in '/data/results/{collection}_{date}.json'")
query_parser.add_argument(
    'q', help="Defines a query using standard query syntax. This parameter is mandatory", required=True)
query_parser.add_argument(
    'q.op', help="Specifies the default operator for query expressions, overriding the default operator specified in the Schema. Possible values are 'AND' or 'OR'.")
query_parser.add_argument(
    'fq', help="Applies a filter query to the search results")
query_parser.add_argument(
    'sort', help="Sorts the response to a query in either ascending or descending order based on the response’s score or another specified characteristic")
query_parser.add_argument(
    'start', help="Specifies an offset (by default, 0) into the responses at which Solr should begin displaying content")
query_parser.add_argument(
    'rows', help="Controls how many rows of responses are displayed at a time (default value: 10)")
query_parser.add_argument(
    'fl', help="Limits the information included in a query response to a specified list of fields. The fields need to either be stored='true' or docValues='true'")
query_parser.add_argument(
    'df', help="Specifies a default field, overriding the definition of a default field in the Schema.")
# TODO: Add remaining parameters if needed
# ======================================================
# Methods
# ======================================================


@api.route('/createCollection/')
class CreateCollection(Resource):
    @api.doc(parser=parser)
    # serialize the output into a response body
    @api.marshal_with(coll, code=200)
    def post(self):
        args = parser.parse_args()
        collection = args['collection']
        corpus, err = sc.create_collection(col_name=collection)
        if err == 409:
            return f"Collection {collection} already exists.", err
        else:
            return corpus, err


@api.route('/deleteCollection/')
class DeleteCollection(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        collection = args['collection']
        sc.delete_collection(col_name=collection)
        return '', 200


@api.route('/listCollections/')
class ListCollections(Resource):
    @api.marshal_with(coll, code=200)
    def get(self):
        return sc.list_collections()


@api.route('/query/')
class Query(Resource):
    @api.doc(parser=query_parser)
    def get(self):
        args = query_parser.parse_args()
        collection = args['collection']
        results_file_path = args['results_file_path']
        q = args['q']
        query_values = {
            'q_op': args['q.op'],
            'fq': args['fq'],
            'sort': args['sort'],
            'start': args['start'],
            'rows': args['rows'],
            'fl': args['fl'],
            'df': args['df']
        }

        if q is None:
            return "Query is mandatory", 400

        if collection is None:
            return "Collection is mandatory", 400

        if results_file_path is None:
            results_file_path = f"/data/results/{collection}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Remove all key-value pairs with value of None
        query_values = {k: v for k, v in query_values.items() if v is not None}

        # Execute query
        code, results = sc.execute_query(
            q=q, col_name=collection, **query_values)

        # Serializing json
        json_object = json.dumps(results.docs, indent=4)

        # Save results to json file
        with open(results_file_path, 'w', encoding='utf-8') as f:
            f.write(json_object)

        return code
