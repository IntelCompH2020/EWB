from flask_restx import Namespace, Resource, fields

api = Namespace('corpora', description='Corpora related operations')

# corpus = api.model('Corpus', {
#     'name': fields.String(required=True,
#                           description='The corpus name'),
#     'ndocs': fields.String(required=True,
#                            description='The number of documents in the corpus')
# })


# @api.route('/indexCorpus/')
# class CreateCollection(Resource):
#     @api.doc(parser=parser)
#     @api.marshal_with(coll, code=200)
#     def post(self):
#         args = parser.parse_args()
#         collection = args['collection']
#         return sc.create_collection(col_name=collection)
