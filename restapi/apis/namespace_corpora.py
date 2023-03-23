from flask_restx import Namespace, Resource, fields

api = Namespace('corpora', description='Corpora related operations')

doc = api.model('Doc', {
    'id': fields.String(required=True, description='The doc indentifier')
})

@api.route('/')
class CatList(Resource):
    @api.doc('list_docs')
    @api.marshal_list_with(doc)
    def get(self):
        '''List all cats'''
        DOCS = [
            {'id': '1'},
        ]
        return DOCS