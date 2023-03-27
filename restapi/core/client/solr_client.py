import os

import requests

from core.entities.corpus import Corpus

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

    def __init__(self, resp, logger):
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
        self.status_code = 400
        self.data = []
        # If response header has status 0, request is acknowledged
        if 'responseHeader' in resp and resp['responseHeader']['status'] == 0:
            logger.info('-- -- Request acknowledged')
            self.status_code = 200
        else:
            # If there is an error in response header, set status code and text attributes accordingly
            self.status_code = resp['responseHeader']['status']
            self.text = resp['error']['msg']
            logger.error(
                f'-- -- Request generated an error {self.status_code}: {self.text}')
        # If collections are returned in response, set data attribute to collections list
        if 'collections' in resp:
            self.data = resp['collections']
            

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
        self.logger = logger

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
            "Created collection {}".format(col_name), SolrResp(resp, self.logger))

        return [{'name': col_name}], sc

    def delete_collection(self, col_name: str):
        """
        Deletes a Solr collection with the given name.
        Returns a list with a dictionary containing the name of the deleted collection and the HTTP status code.
        """

        resp = requests.get(
            url='{}/api/collections?action=DELETE&name={}'.format(self.solr_url, col_name), timeout=10)

        _, sc = self.resp_msg(
            "Collection {} deleted succesfully".format(col_name), SolrResp(resp, self.logger))

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
            "Collection listing carried out succesfully", SolrResp(resp, self.logger))

        collections_dicts = [{"name": coll} for coll in colls]

        return collections_dicts, sc

    def index_batch(self, docs_batch: list[dict], col_name: str, to_index: int, index_from: int, index_to: int):

        headers_ = {'Content-type': 'application/json'}
        data = {"add": docs_batch}

        resp = requests.post(
            url='{}/solr/{}/update'.format(self.solr_url, col_name), headers=headers_, json=data, timeout=10)

        _, sc = self.resp_msg(
            "Indexed documents from {} to {} / {} in Collection '{}'".format(index_from, index_to, to_index, col_name), SolrResp(resp, self.logger))

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

    # def index_documents(documents_filename, embedding_filename):
    #     # Open the file containing text.
    #     with open(documents_filename, "r") as documents_file:
    #         # Open the file containing vectors.
    #         with open(embedding_filename, "r") as vectors_file:
    #             documents = []
    #             # For each document creates a JSON document including
    #             both text and related vector.
    #             for index, (document, vector_string) in enumerate
    #             (zip(documents_file, vectors_file)):

    #                 vector =
    #                 [float(w) for w in vector_string.split(",")]
    #                 doc = {
    #                     "id": str(index),
    #                     "text": document,
    #                     "vector": vector
    #                 }
    #                 # Append JSON document to a list.
    #                 documents.append(doc)

    #                 # To index batches of documents at a time.
    #                 if index % BATCH_SIZE == 0 and index != 0:
    #                     # How you'd index data to Solr.
    #                     solr.add(documents)
    #                     documents = []
    #                     print("==== indexed {} documents ======"
    #                     .format(index))
    #             # To index the rest, when 'documents' list < BATCH_SIZE.
    #             if documents:
    #                 solr.add(documents)
    #             print("finished")

    ############################################################################

    def delete_index(self, index):
        params = {
            'action': 'UNLOAD',
            'core': index,
            'deleteIndex': 'true',
            'deleteDataDir': 'true',
            'deleteInstanceDir': 'true'
        }

        resp = requests.get(
            '{}/admin/cores?'.format(self.solr_base_ep), params=params)
        self.resp_msg("Deleted index {}".format(index), SolrResp(resp))

    def create_index(self, index_name, index_spec):
        # Presumes there is a link between the docker container and the 'index'
        # directory under docker/solr/ (ie docker/solr/tmdb/ is linked into
        # Docker container configsets)
        params = {
            'action': 'CREATE',
            'name': index_name,
            'configSet': index_spec,
        }
        resp = requests.get(
            '{}/admin/cores?'.format(self.solr_base_ep), params=params)

        self.resp_msg("Created index {}".format(index_name), SolrResp(resp))

    def index_documents(self, index, doc_src):
        def commit():
            print('Committing changes')
            resp = requests.get(
                '{}/{}/update?commit=true'.format(self.solr_base_ep, index))
            self.resp_msg("Committed index {}".format(index), resp)

        def flush(docs):
            print('Flushing {} docs'.format(len(docs)))
            resp = requests.post('{}/{}/update'.format(
                self.solr_base_ep, index), json=docs)
            self.resp_msg("Done", resp)
            docs.clear()

        BATCH_SIZE = 5000
        docs = []
        for doc in doc_src:
            if 'release_date' in doc and doc['release_date'] is not None:
                doc['release_date'] += 'T00:00:00Z'

            docs.append(doc)

            if len(docs) % BATCH_SIZE == 0:
                flush(docs)

        flush(docs)
        commit()

    def query(self, index, query):
        url = '{}/{}/select?'.format(self.solr_base_ep, index)

        resp = requests.post(url, data=query)
        #resp_msg(msg='Query {}...'.format(str(query)[:20]), resp=resp)
        resp = resp.json()

        qtime = resp['responseHeader']['QTime']
        numfound = resp['response']['numFound']

        return resp['response']['docs'], qtime, numfound

    def analyze(self, index, fieldtype, text):
        # http://localhost:8983/solr/msmarco/analysis/field
        url = '{}/{}/analysis/field?'.format(self.solr_base_ep, index)

        query = {
            "analysis.fieldtype": fieldtype,
            "analysis.fieldvalue": text
        }

        resp = requests.post(url, data=query)

        analysis_resp = resp.json()
        tok_stream = analysis_resp['analysis']['field_types']['text_general']['index']
        tok_stream_result = tok_stream[-1]
        return tok_stream_result

    def term_vectors_skip_to(self, index, q='*:*', skip=0):
        url = '{}/{}/tvrh/'.format(self.solr_base_ep, index)
        query = {
            'q': q,
            'cursorMark': '*',
            'sort': 'id asc',
            'fl': 'id',
            'rows': str(skip)
        }
        tvrh_resp = requests.post(url, data=query)
        return tvrh_resp.json()['nextCursorMark']

    def get_doc(self, index, doc_id):
        params = {
            'q': 'id:{}'.format(doc_id),
            'wt': 'json'
        }

        resp = requests.post(
            '{}/{}/select'.format(self.solr_base_ep, index), data=params).json()
        return resp['response']['docs'][0]
