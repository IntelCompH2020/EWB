"""
This script defines a Flask RESTful namespace for performing classification.

Author: Lorena Calvo-Bartolomé
Date: 07/08/2023
"""

from flask_restx import Namespace, Resource, reqparse
from src.core.ewb_classifier import EWBClassifier
import logging
logging.basicConfig(level='DEBUG')
logger = logging.getLogger('Classifier')

# ======================================================
# Define namespace for classification operations
# ======================================================
api = Namespace('Classification operations')
classifier = EWBClassifier(logger)

# ======================================================
# Define parsers to take inputs from user
# ======================================================
classify_parser = reqparse.RequestParser()
classify_parser.add_argument('text',
                              help='Text to be classified',
                              required=True)
classify_parser.add_argument('taxonmy',
                              help='Taxonomy to be used for the classification', required=True)

cache_models_parser = reqparse.RequestParser()
cache_models_parser.add_argument('taxonmy',
                                help='Taxonomy to be used for the classification', required=True)

@api.route('/classify/')
class Classify(Resource):
    @api.doc(parser=classify_parser)
    def post(self):
        args = classify_parser.parse_args()
        text = args['text']
        taxonomy = args['taxonmy']
        try:
            return classifier.classify(text, taxonomy), 200
        except Exception as e:
            return str(e), 500
    
@api.route('/list_avail_taxonomies/')
class ListAvailTaxonomies(Resource):
    def post(self):
        try:
            return classifier.get_avail_taxonomies()
        except Exception as e:
            return str(e), 500

@api.route('/cache_models/')
class CacheModels(Resource):
    @api.doc(parser=cache_models_parser)
    def post(self):
        args = cache_models_parser.parse_args()
        try:
            classifier.cache_models(args['taxonmy'])
            return f"Models associated with axonomy {args['taxonmy']} were loaded in the cache direcotory", 200
        except Exception as e:
            return str(e), 500
        
@api.route('/list_models')
class ListModels(Resource):
    def post(self):
        try:
            return classifier.list_models()
        except Exception as e:
            return str(e), 500       

@api.route('/list_classes')
class ListClasses(Resource):
    def post(self):
        try:
            return classifier.list_classes()
        except Exception as e:
            return str(e), 500