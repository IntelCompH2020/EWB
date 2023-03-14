import os
import sys
from datetime import datetime

import requests
from flask import Flask
from flask_restx import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage

from flask.logging import create_logger
from flask.logging import default_handler
from flask.logging import logging as flask_logging

# Create Flask app
app = Flask(__name__)
api = Api(app)

# Create logger
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

logger = create_logger(app)
logger.addHandler(default_handler)
logger.setLevel(flask_logging.DEBUG)

# Configure Flask-Logging to save logs to a file
app.config["LOGGING_FILE_PATH"] = log_filepath
app.config["LOGGING_FILE_ENABLED"] = True
app.config["LOGGING_FILE_LEVEL"] = "DEBUG"

parser = reqparse.RequestParser()
parser.add_argument('name', help='Specify your name')


@api.route('/hello/')
class HelloWorld(Resource):
    @api.doc(parser=parser)
    def get(self):
        args = parser.parse_args()
        name = args['name']
        return "Hello " + name


upload_parser = api.parser()
upload_parser.add_argument('file',
                           location='files',
                           type=FileStorage)


@api.route('/upload/')
@api.expect(upload_parser)
class UploadDemo(Resource):
    def post(self):
        args = upload_parser.parse_args()
        file = args.get('file')
        print(file.filename)
        return "Uploaded file is " + file.filename


parser2 = reqparse.RequestParser()
parser2.add_argument('collection', help='Specify collection name')


@api.route('/createCollection/')
class CreateCollection(Resource):
    @api.doc(parser=parser2)
    def post(self):
        args = parser2.parse_args()
        collection = args['collection']
        url_ = 'http://solr:8983/api/collections'
        headers_ = {"Content-Type": "application/json"}
        data = {
            "create": {
                "name": collection,
                "numShards": 1,
                "replicationFactor": 1
            }
        }

        try:
            response = requests.post(
                url=url_, headers=headers_, json=data, timeout=10)
            response.raise_for_status()
            app.logger.info('-- -- Request succeded')
        except requests.exceptions.HTTPError as errh:
            app.logger.error(errh)
        except requests.exceptions.ConnectionError as errc:
            app.logger.error(errc)
        except requests.exceptions.Timeout as errt:
            app.logger.error(errt)
        except requests.exceptions.RequestException as err:
            app.logger.error(err)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
