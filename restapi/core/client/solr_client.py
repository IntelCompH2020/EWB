"""
This  module provides classes to handle Solr API responses and requests.

The SolrResults class is for wrapping decoded Solr responses, where individual documents can be retrieved either through the docs attribute or by iterating over the instance. 

The SolrResp class is for handling Solr API response and errors. 

The SolrClient class is for handling Solr API requests. 

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

import logging
import os

import requests

from core.entities.corpus import Corpus
from core.entities.model import Model
from urllib import parse


BATCH_SIZE = 100
CORPUS_COL = "Corpora"


class SolrResults(object):
    """Class for wrapping decoded (from JSON) solr responses.

    Individual documents can be retrieved either through ``docs`` attribute
    or by iterating over results instance.
    """

    def __init__(self,
                 json_response: dict,
                 next_page_query: bool = None):
        """Init method.

        Parameters
        ----------
        json_response: dict
            JSON response from Solr.
        next_page_query: bool, defaults to None
            If True, then the next page of results is fetched.
        """
        self.solr_json_response = json_response

        # Main response part of decoded Solr response
        response = json_response.get("response") or {}
        self.docs = response.get("docs", ())
        self.hits = response.get("numFound", 0)

        # other response metadata
        self.debug = json_response.get("debug", {})
        self.highlighting = json_response.get("highlighting", {})
        self.facets = json_response.get("facet_counts", {})
        self.spellcheck = json_response.get("spellcheck", {})
        self.stats = json_response.get("stats", {})
        self.qtime = json_response.get("responseHeader", {}).get("QTime", None)
        self.grouped = json_response.get("grouped", {})
        self.nextCursorMark = json_response.get("nextCursorMark", None)
        self._next_page_query = (
            self.nextCursorMark is not None and next_page_query or None
        )

    def __len__(self):
        """

        """
        if self._next_page_query:
            return self.hits
        else:
            return len(self.docs)

    def __iter__(self):
        """

        """
        result = self
        while result:
            for d in result.docs:
                yield d
            result = result._next_page_query and result._next_page_query()


class SolrResp(object):
    """
    A class to handle Solr API response and errors.

    Examples
    --------
        # From delete collection
        response = {
                    "responseHeader":{
                        "status":0,
                        "QTime":1130}
                    }
        # From query
        response = {
                    "responseHeader":{
                        "zkConnected":true,
                        "status":0,
                        "QTime":15,
                        "params":{
                        "q":"*:*",
                        "indent":"true",
                        "q.op":"OR",
                        "useParams":"",
                        "_":"1681211825934"
                    }},
                        "response":{
                            "numFound":3,
                            "start":0,
                            "numFoundExact":true,
                            'docs': [{'id': 1}, {'id': 2}, {'id': 3}]
                      }}
    """

    def __init__(self,
                 status_code: int,
                 text: str,
                 data: list,
                 results: SolrResults = None):
        """Init method.

        Parameters
        ----------
        status_code: int
            The status code of the Solr API response.
        text: str
            The text of the Solr API response.
        data: list
            A list of dictionaries that represents the data returned by the Solr API response (e.g., when list_collections is used)
        results: SolrResults
            A SolrResults object that represents the data returned by the Solr API response, only under the condition that "response" is in the JSON dict returned by Solr (e.g., when performing a query)
        """
        self.status_code = status_code
        self.text = text
        self.data = data
        self.results = results

    @staticmethod
    def from_error(status_code: int, text: str):
        return SolrResp(status_code, text, [])

    @staticmethod
    def from_requests_response(resp: requests.Response, logger: logging.Logger):
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
        results = {}

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

        if 'response' in resp:
            results = SolrResults(resp, True)

        return SolrResp(status_code, text, data, results)


class SolrClient(object):
    """
    A class to handle Solr API requests.
    """

    def __init__(self, logger: logging.Logger):
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
        # self.logger = logger
        import logging
        logging.basicConfig(level='DEBUG')
        self.logger = logging.getLogger('Solr')

    def _do_request(self,
                    type: str,
                    url: str,
                    timeout: int = 10,
                    **params) -> SolrResp:
        """Sends a requests to the given url with the given params and returns an object of the SolrResp class

        Parameters
        ----------
        type: str
            The type of request to send.
        url: str
            The url to send the request to.
        timeout: int, defaults to 10
            The timeout in seconds to use for the request.

        Returns
        -------
        SolrResp : SolrResp
            The response object.
        """

        # Send request
        if type == "get":
            resp = requests.get(
                url=url,
                timeout=timeout,
                **params
            )
            pass
        elif type == "post":
            resp = requests.post(
                url=url,
                timeout=timeout,
                **params
            )
        else:
            self.logger.error(f"Invalid type {type}")
            return

        # Parse Solr request
        solr_resp = SolrResp.from_requests_response(resp, self.logger)

        return solr_resp

    # ======================================================
    # MANAGING (Creation, deletion, listing, etc.)
    # ======================================================
    def add_vector_field_to_schema(self,
                                   col_name: str,
                                   field_name: str):
        """Adds a field of type 'VectorField' to the schema of the collection given by 'col_name'. 
        """

        headers_ = {"Content-Type": "application/json"}
        data = {
            "add-field": {
                "name": field_name,
                "type": "VectorField",
                "indexed": "true",
                "termOffsets": "true",
                "stored": "true",
                "termPositions": "true",
                "termVectors": "true",
                "multiValued": "true"
            }
        }
        url_ = '{}/api/collections/{}/schema?'.format(self.solr_url, col_name)

        # Send request to Solr
        solr_resp = self._do_request(type="post", url=url_,
                                     headers=headers_, json=data)

        return [{'name': col_name}], solr_resp.status_code

    def create_collection(self,
                          col_name: str,
                          config: str = 'ewb_config',
                          nshards: int = 1,
                          replicationFactor: int = 1):
        """Creates a Solr collection with the given name, config, number of shards, and replication factor.
        Returns a list with a dictionary containing the name of the created collection and the HTTP status code.
        """

        # Check if collection already exists
        colls, _ = self.list_collections()
        colls_names = [d["name"] for d in colls]
        if col_name in colls_names:
            solr_resp = SolrResp.from_error(
                409, "Collection {} already exists".format(col_name))
            return _, solr_resp.status_code

        # Carry on with creation if collection does not exists
        headers_ = {"Content-Type": "application/json"}
        data = {
            "create": {
                "name": col_name,
                "config": config,
                "numShards": nshards,
                "replicationFactor": replicationFactor
            }
        }
        url_ = '{}/api/collections?'.format(self.solr_url)

        # Send request to Solr
        solr_resp = self._do_request(type="post", url=url_,
                                     headers=headers_, json=data)

        return [{'name': col_name}], solr_resp.status_code

    def delete_collection(self, col_name: str):
        """
        Deletes a Solr collection with the given name.
        Returns a list with a dictionary containing the name of the deleted collection and the HTTP status code.
        """

        url_ = '{}/api/collections?action=DELETE&name={}'.format(
            self.solr_url, col_name)

        # Send request to Solr
        solr_resp = self._do_request(type="get", url=url_)

        return [{'name': col_name}], solr_resp.status_code

    def list_collections(self, type=None):
        """
        Lists all Solr collections. If type is given, only lists the collections associated with the given type. E.g., if type = "corpus", and Solr holfs the collections "Corpus_Cordis" and "Model_Mallet-25", only the first of the latter will be returned.
        Returns a list of dictionaries, where each dictionary has a key "name" with the value of the collection name,
        and the HTTP status code.
        """

        url_ = '{}/api/collections'.format(self.solr_url)

        # Send request to Solr
        solr_resp = self._do_request(type="get", url=url_)

        # Get collections in the format required my the Collection namespace
        if type:
            collections_dicts = [{"name": coll}
                                 for coll in solr_resp.data
                                 if coll.split("_")[0].lower() == type.lower()]

        else:
            collections_dicts = [{"name": coll} for coll in solr_resp.data]

        return collections_dicts, solr_resp.status_code

    def index_batch(self,
                    docs_batch: list[dict],
                    col_name: str,
                    to_index: int,
                    index_from: int,
                    index_to: int):
        """Takes a batch of documents, a Solr collection name, and the indices of the batch to be indexed, and sends a POST request to the Solr server to index the documents. The method returns the status code of the response.

        Parameters
        ----------
        docs_batch : list[dict])
            A list of dictionaries where each dictionary represents a document to be indexed.
        col_name : str
            The name of the Solr collection to index the documents into.
        to_index : int
            The total number of documents to be indexed.
        index_from :int
            The starting index of the documents in the batch to be indexed.
        index_to: int
            The ending index of the documents in the batch to be indexed.

        Returns
        -------
        sc : int
            The status code of the response.
        """

        headers_ = {'Content-type': 'application/json'}

        params = {
            'commitWithin': '1000',
            'overwrite': 'true',
            'wt': 'json'
        }

        url_ = '{}/solr/{}/update'.format(self.solr_url, col_name)

        # Send request to Solr
        solr_resp = self._do_request(
            type="post", url=url_, headers=headers_, json=docs_batch,
            params=params, proxies={})

        if solr_resp.status_code == 200:
            self.logger.info(
                f"Indexed documents from {index_from} to {index_to} / {to_index} in Collection '{col_name}'")

        return solr_resp.status_code

    # ======================================================
    # INDEXING
    # ======================================================

    def index_documents(self,
                        json_docs: list[dict],
                        col_name: str):
        """It takes a list of documents in JSON format and a Solr collection name, splits the list into batches, and sends a POST request to the Solr server to index the documents in batches. The method returns the status code of the response.

        Parameters
        ----------
        json_docs : list[dict]
            A list of dictionaries where each dictionary represents a document to be indexed.
        col_name : str 
            The name of the Solr collection to index the documents into.

        Returns
        -------
        sc : int
            The status code of the response.    
        """

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

    def index_corpus(self, corpus_logical_name: str):
        """Given the logical name of a corpus file (i.e., if we have a logical corpus named 'Cordis.json', corpus_logical_name should be 'Cordis'), it creates a Solr collection with such a name, reades the corpus file, extracts the raw information of each document, and sends a POST request to the Solr server to index the documents in batches.

        Parameters
        ----------
        corpus_logical_name : str
            The logical name of the corpus file to be indexed. The file should be located at /data/source/ directory.
        col_name : str
            The name of the Solr collection to index the documents into.
        """

        corpus_to_index = "/data/source/" + corpus_logical_name + ".json"

        # 1. Create collection
        corpus, err = self.create_collection(col_name=corpus_logical_name)
        if err == 409:
            self.logger.info(
                f"Collection {corpus_logical_name} already exists.")
            return
        else:
            self.logger.info(
                f"Collection {corpus_logical_name} successfully created.")

        # 2. Add corpus collection to CORPUS_COL. If Corpora has not been created already, create it
        corpus, err = self.create_collection(col_name=CORPUS_COL)
        if err == 409:
            self.logger.info(
                f"Collection {CORPUS_COL} already exists.")
            # 2.1. Do query to retrieve last id in CORPUS_COL
            # http://localhost:8983/solr/#/{CORPUS_COL}/query?q=*:*&q.op=OR&indent=true&sort=id desc&fl=id&rows=1&useParams=

            sc, results = self.execute_query(q='*:*',
                                             sort="id desc",
                                             rows="1",
                                             fl="id")
            self.logger.info(results.docs)
            corpus_id = results.docs["id"]
            self.logger.info(corpus_id)

            # Increment corpus_id for next corpus to be indexed
            corpus_id += 1

        else:
            self.logger.info(
                f"Collection {CORPUS_COL} successfully created.")
            corpus_id = 1

        # 3. Create Corpus object and extract info from the corpus to index
        corpus = Corpus(corpus_to_index)
        json_docs = corpus.get_docs_raw_info()
        corpus_col_upt = corpus.get_corpora_update(id=corpus_id)

        # 4. Index corpus and its fiels in CORPUS_COL
        self.logger.info(
            f"Indexing of {corpus_logical_name} info in {CORPUS_COL} starts.")
        self.index_documents(corpus_col_upt, CORPUS_COL)
        self.logger.info(
            f"Indexing of {corpus_logical_name} info in {CORPUS_COL} completed.")

        # 5. Index documents in corpus collection
        self.logger.info(
            f"Indexing of {corpus_logical_name} in {corpus_logical_name} starts.")
        self.index_documents(json_docs, corpus_logical_name)
        self.logger.info(
            f"Indexing of {corpus_logical_name} in {corpus_logical_name} completed.")

        return

    def index_model(self, model_name: str):
        """
        Given the name of a model created with the ITMT (i.e., the name of one of the folders representing a model within the TMmodels folder), it extracts the model information and that of the corpus used for its generation. It then adds a new field in the corpus collection of type 'VectorField' and name 'doctpc_{model_name}, and index the document-topic proportions in it. At last, it index the rest of the model information in the model collection.

        Parameters
        ----------
        model_name : str
            The name of the model file to be indexed. The file should be located at /data/source/ directory.
        """

        model_to_index = "/data/source/" + model_name

        # 1. Create collection
        corpus, err = self.create_collection(col_name=model_name)
        if err == 409:
            self.logger.info(
                f"Collection {model_name} already exists.")
            return
        else:
            self.logger.info(
                f"Collection {model_name} successfully created.")

        # 2. Create Model object and extract info from the corpus to index
        model = Model(model_to_index)
        json_docs, corpus_name = model.get_model_info_update()
        field_update = model.get_corpora_model_update()

        # 3. Add field for the doc-tpc distribution associated with the model being indexed in the document associated with the corpus
        self.logger.info(
            f"Indexing model inforamtion of {model_name} in {CORPUS_COL} starts.")
        self.index_documents(field_update, CORPUS_COL)
        self.logger.info(
            f"Indexing of model inforamtion of {model_name} info in {CORPUS_COL} completed.")

        # 4. Modify schema in corpus collection to add field for the doc-tpc distribution associated with the model being indexed
        model_key = 'doctpc_' + model_name
        self.logger.info(
            f"Adding field {model_key} in {corpus_name} collection")
        corpus, err = self.add_vector_field_to_schema(
            corpus_name, model_key)
        self.logger.info(corpus)
        self.logger.info(err)

        # 5. Index doc-tpc information in corpus collection
        self.logger.info(
            f"Indexing model information in {corpus_name} collection")
        self.index_documents(json_docs, corpus_name)

        self.logger.info(
            f"Indexing model information in {model_name} collection")
        json_tpcs = model.get_model_info()
        self.index_documents(json_tpcs, model_name)

    def delete_corpus(self, corpus_logical_name: str):
        # TODO: Implement me
        # 1. Delete corpus collection
        _, sc = self.delete_collection(col_name=corpus_logical_name)

        # 2. Get ID and associated models of corpus collection in CORPUS_COL
        sc, results = self.execute_query(q='corpus_name:{corpus_logical_name}',
                                         fl="id,models")
        self.logger.info(results.docs)

        # 3. Delete all models associated with the corpus
        for model in results.docs["models"]:
            pass

        # 4. Remove corpus from CORPUS_COL
        # Generate update with { "delete":"myid" }

        return

    def delete_model(self):

        # 1. Delete model collection

        # 2. Generate update with get_corpora_model_update & delete to delete tpc-distric field in field and model from models in corpus collection within CORPUS_COL

        # 3. Generate update with get_model_info_update & delete (add the field to action:str to be customizable btwn set and delete) to remove model infromation from corpus collection

        return

    # ======================================================
    # QUERIES
    # ======================================================
    def execute_query(self, q: str, col_name: str, **kwargs):
        """ 
        Performs a query and returns the results.

        Requires a ``q`` for a string version of the query to run. Optionally accepts ``**kwargs``for additional options to be passed through the Solr URL.

        Parameters
        ----------
        q:
        col_name:


        Usage
        -----
            # All docs
            results = solr.search('*:*')
        """

        # Prepare query
        params = {"q": q}
        params.update(kwargs)

        # We want the result of the query as json
        params["wt"] = "json"

        # Encode query
        query_string = parse.urlencode(params)

        url_ = '{}/solr/{}/select?{}'.format(self.solr_url,
                                             col_name, query_string)

       # Send query to Solr
        solr_resp = self._do_request(type="get", url=url_)

        return solr_resp.status_code, solr_resp.results
    

class EWBSolrClient(SolrClient):
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        
        # TODO: Implement here only the methods that are directly related with the EWB and leave the others in the generic class
