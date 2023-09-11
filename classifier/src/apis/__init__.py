from flask_restx import Api

from .namespace_classify import api as ns1

api = Api(
    title='Classifier API',
    version='1.0',
    description='A description',
)

api.add_namespace(ns1, path='/classification')