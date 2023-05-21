from flask_restx import Api

from .namespace_infer import api as ns1

api = Api(
    title='Inferencer API',
    version='1.0',
    description='A description',
)

api.add_namespace(ns1, path='/inference_operations')
