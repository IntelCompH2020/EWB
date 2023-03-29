import os

import requests

from core.entities.corpus import Corpus
from core.entities.model import Model

BATCH_SIZE = 100


class SolrResp:
    """
    A class to handle Solr API response and errors.

    Attributes
    ----------
    status_code : int
        The status code of the Solr API response.
    data : list
        A list of dictionaries that represents the data returned by the Solr API response.

    Methods
    -------
    __init__(self, resp, logger):
        Initializes SolrResp instance.
    """

    def __init__(self, status_code, text, data):
        self.status_code = status_code
        self.text = text
        self.data = data

    @staticmethod
    def from_error(status_code, text):
        return SolrResp(status_code, text, [])

    @staticmethod
    def from_requests_response(resp, logger):
        """
        Parameters
        ----------
        resp : requests.Response
            The Solr API response.
        logger : logging.Logger
            The logger object to log messages and errors.
        """

        # Parse the response and set status code and data attributes accordingly
        resp = resp.json()
        status_code = 400
        data = []
        text = ""
        # If response header has status 0, request is acknowledged
        if 'responseHeader' in resp and resp['responseHeader']['status'] == 0:
            logger.info('-- -- Request acknowledged')
            status_code = 200
        else:
            # If there is an error in response header, set status code and text attributes accordingly
            status_code = resp['responseHeader']['status']
            text = resp['error']['msg']
            logger.error(
                f'-- -- Request generated an error {status_code}: {text}')
        # If collections are returned in response, set data attribute to collections list
        if 'collections' in resp:
            data = resp['collections']

        return SolrResp(status_code, text, data)


class SolrClient():
    """
    A class to handle Solr API requests.

    Attributes
    ----------
    solr_url : str
        The Solr URL.
    solr : requests.Session
        The requests session to use for Solr requests.
    logger : logging.Logger
        The logger object to log messages and errors.

    Methods
    -------
    resp_msg(msg: str, resp: SolrResp):
        Returns the data and status code of the Solr API response.
    create_collection(col_name: str, config: str = 'ewb_config', nshards: int = 1, replicationFactor: int = 1):
        Creates a Solr collection.
    delete_collection(col_name: str):
        Deletes a Solr collection.
    list_collections():
        Returns a list of dictionaries that contains the name of each collection.
    """

    def __init__(self, logger):
        """
        Parameters
        ----------
        logger : logging.Logger
            The logger object to log messages and errors.
        """

        # Get the Solr URL from the environment variables
        self.solr_url = os.environ.get('SOLR_URL')

        # Initialize requests session and logger
        self.solr = requests.Session()
        #self.logger = logger
        import logging
        logging.basicConfig(level='DEBUG')
        self.logger = logging.getLogger('Solr')

    @staticmethod
    def resp_msg(msg: str, resp: SolrResp):
        """
        Returns the data and status code of the Solr API response.

        Parameters
        ----------
        msg : str
            The message to log.
        resp : SolrResp
            The Solr API response object.

        Returns
        -------
        list
            A list of dictionaries that represents the data returned by the Solr API response.
        int
            The status code of the Solr API response.
        """
        print('resp_msg: {} [Status: {}]'.format(msg, resp.status_code))
        return resp.data, resp.status_code

    def create_collection(self, col_name: str, config: str = 'ewb_config', nshards: int = 1, replicationFactor: int = 1):
        """
        Creates a Solr collection with the given name, config, number of shards, and replication factor.
        Returns a list with a dictionary containing the name of the created collection and the HTTP status code.
        """

        # Check if collection already exists
        colls, _ = self.list_collections()
        colls_names = [d["name"] for d in colls]
        if col_name in colls_names:
            _, sc = self.resp_msg(
                "Collection {} already exists".format(col_name), SolrResp.from_error(409, "Collection {} already exists".format(col_name)))
            return _, sc

        headers_ = {"Content-Type": "application/json"}
        data = {
            "create": {
                "name": col_name,
                "config": config,
                "numShards": nshards,
                "replicationFactor": replicationFactor
            }
        }
        resp = requests.post(
            url='{}/api/collections?'.format(self.solr_url), headers=headers_, json=data, timeout=10)

        _, sc = self.resp_msg(
            "Created collection {}".format(col_name), SolrResp.from_requests_response(resp, self.logger))

        return [{'name': col_name}], sc

    def delete_collection(self, col_name: str):
        """
        Deletes a Solr collection with the given name.
        Returns a list with a dictionary containing the name of the deleted collection and the HTTP status code.
        """

        resp = requests.get(
            url='{}/api/collections?action=DELETE&name={}'.format(self.solr_url, col_name), timeout=10)

        _, sc = self.resp_msg(
            "Collection {} deleted succesfully".format(col_name), SolrResp.from_requests_response(resp, self.logger))

        return [{'name': col_name}], sc

    def list_collections(self):
        """
        Lists all Solr collections.
        Returns a list of dictionaries, where each dictionary has a key "name" with the value of the collection name,
        and the HTTP status code.
        """

        resp = requests.get(
            url='{}/api/collections'.format(self.solr_url), timeout=10)

        colls, sc = self.resp_msg(
            "Collection listing carried out succesfully", SolrResp.from_requests_response(resp, self.logger))

        collections_dicts = [{"name": coll} for coll in colls]

        return collections_dicts, sc

    def index_batch(self, docs_batch: list[dict], col_name: str, to_index: int, index_from: int, index_to: int):

        headers_ = {'Content-type': 'application/json'}

        params = {
            'commitWithin': '1000',
            'overwrite': 'true',
            'wt': 'json'
        }

        resp = requests.post(
            url='{}/solr/{}/update'.format(self.solr_url, col_name), headers=headers_, json=docs_batch, timeout=10, params=params, proxies={})

        _, sc = self.resp_msg(
            "Indexed documents from {} to {} / {} in Collection '{}'".format(index_from, index_to, to_index, col_name), SolrResp.from_requests_response(resp, self.logger))

        return sc

    def index_documents(self, json_docs: list[dict], col_name: str):
        docs_batch = []
        index_from = 0
        to_index = len(json_docs)
        for index, doc in enumerate(json_docs):
            docs_batch.append(doc)
            # To index batches of documents at a time.
            if index % BATCH_SIZE == 0 and index != 0:
                # Index batch to Solr
                self.index_batch(docs_batch, col_name, to_index,
                                 index_from=index_from, index_to=index)
                docs_batch = []
                index_from = index + 1
                self.logger.info("==== indexed {} documents ======"
                                 .format(index))
        # To index the rest, when 'documents' list < BATCH_SIZE.
        if docs_batch:
            self.index_batch(docs_batch, col_name, to_index,
                             index_from=index_from, index_to=index)
        self.logger.info("Finished indexing")

        return

    def index_corpus(self, corpus_logical_name: str, col_name: str):
        corpus_to_index = "/data/source/" + corpus_logical_name
        corpus = Corpus(corpus_to_index)
        json_docs = corpus.get_docs_raw_info()

        self.index_documents(json_docs, col_name)

        return
    
    def index_model(self, model_name: str):
        model_to_index = "/data/source/" + model_name
        model = Model(model_to_index)
        
        self.logger.info("Indexing model info in docs")
        json_docs, corpus_col_name = model.get_model_info_update()
        self.index_documents(json_docs, corpus_col_name)

        self.logger.info("Indexing model info in model")
        json_tpcs = model.get_model_info()
        self.index_documents(json_tpcs, model_name)
        