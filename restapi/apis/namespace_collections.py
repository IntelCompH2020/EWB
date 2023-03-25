from flask_restx import Namespace, Resource, fields, reqparse
from core.client.solr_client import SolrClient

RESTX_MASK_SWAGGER = False

# ======================================================
# Define namespace for managing collections
# ======================================================
api = Namespace('Collections',
                description='Solr collections related operations')

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
sc = SolrClient(api.logger)

# Define parser to take inputs from user
parser = reqparse.RequestParser()
parser.add_argument('collection', help='Specify collection name')

# ======================================================
# Methods
# ======================================================


@api.route('/createCollection/')
class CreateCollection(Resource):
    @api.doc(parser=parser)
    @api.marshal_with(coll, code=200)
    def post(self):
        args = parser.parse_args()
        collection = args['collection']
        return sc.create_collection(col_name=collection)


@api.route('/deleteCollection/')
class DeleteCollection(Resource):
    @api.doc(parser=parser)
    @api.marshal_with(coll, code=200)
    def post(self):
        args = parser.parse_args()
        collection = args['collection']
        return sc.delete_collection(col_name=collection)


@api.route('/listCollections/')
class ListCollections(Resource):
    @api.marshal_with(coll, code=200)
    def post(self):
        return sc.list_collections()
