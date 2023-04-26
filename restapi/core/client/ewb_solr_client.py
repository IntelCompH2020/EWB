"""
This module provides a specific class for handeling the Solr API responses and requests of the EWB.

Author: Lorena Calvo-Bartolomé
Date: 17/04/2023
"""

import configparser
import logging
import pathlib

from core.client.base.solr_client import SolrClient
from core.entities.queries import Queries
from core.entities.corpus import Corpus
from core.entities.model import Model


class EWBSolrClient(SolrClient):

    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = "core/client/config/config.cf"):
        super().__init__(logger)

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self.batch_size = int(cf.get('restapi', 'batch_size'))
        self.corpus_col = cf.get('restapi', 'corpus_col')

        # Create Queries object for managing queries
        self.querier = Queries()

    # ======================================================
    # CORPUS-RELATED OPERATIONS
    # ======================================================
    def index_corpus(self,
                     corpus_logical_path: str):
        """Given the string path of corpus file, it creates a Solr collection with such the stem name of the file (i.e., if we had '/data/source.Cordis.json' as corpus_logical_path, 'Cordis' would be the stem), reades the corpus file, extracts the raw information of each document, and sends a POST request to the Solr server to index the documents in batches.

        Parameters
        ----------
        corpus_logical_path : str
            The path of the logical corpus file to be indexed.
        """

        # 1. Get full path and stem of the logical corpus
        corpus_to_index = pathlib.Path(corpus_logical_path)
        corpus_logical_name = corpus_to_index.stem

        # 2. Create collection
        corpus, err = self.create_collection(col_name=corpus_logical_name)
        if err == 409:
            self.logger.info(
                f"-- -- Collection {corpus_logical_name} already exists.")
            return
        else:
            self.logger.info(
                f"-- -- Collection {corpus_logical_name} successfully created.")

        # 3. Add corpus collection to self.corpus_col. If Corpora has not been created already, create it
        corpus, err = self.create_collection(col_name=self.corpus_col)
        if err == 409:
            self.logger.info(
                f"-- -- Collection {self.corpus_col} already exists.")

            # 3.1. Do query to retrieve last id in self.corpus_col
            # http://localhost:8983/solr/#/{self.corpus_col}/query?q=*:*&q.op=OR&indent=true&sort=id desc&fl=id&rows=1&useParams=
            sc, results = self.execute_query(q='*:*',
                                             col_name=self.corpus_col,
                                             sort="id desc",
                                             rows="1",
                                             fl="id")
            if sc != 200:
                self.logger.error(
                    f"-- -- Error getting latest used ID. Aborting operation...")
                return
            # Increment corpus_id for next corpus to be indexed
            corpus_id = results.docs[0]["id"] + 1
        else:
            self.logger.info(
                f"Collection {self.corpus_col} successfully created.")
            corpus_id = 1

        # 4. Create Corpus object and extract info from the corpus to index
        corpus = Corpus(corpus_to_index)
        json_docs = corpus.get_docs_raw_info()
        corpus_col_upt = corpus.get_corpora_update(id=corpus_id)

        # 5. Index corpus and its fiels in CORPUS_COL
        self.logger.info(
            f"-- -- Indexing of {corpus_logical_name} info in {self.corpus_col} starts.")
        self.index_documents(corpus_col_upt, self.corpus_col, self.batch_size)
        self.logger.info(
            f"-- -- Indexing of {corpus_logical_name} info in {self.corpus_col} completed.")

        # 6. Index documents in corpus collection
        self.logger.info(
            f"-- -- Indexing of {corpus_logical_name} in {corpus_logical_name} starts.")
        self.index_documents(json_docs, corpus_logical_name, self.batch_size)
        self.logger.info(
            f"-- -- Indexing of {corpus_logical_name} in {corpus_logical_name} completed.")

        return

    def list_corpus_collections(self) -> list:
        """Returns a list of the names of the corpus collections that have been created in the Solr server.
        """

        sc, results = self.execute_query(q='*:*',
                                         col_name=self.corpus_col,
                                         fl="corpus_name")
        if sc != 200:
            self.logger.error(
                f"-- -- Error getting corpus collections in {self.corpus_col}. Aborting operation...")
            return

        corpus_lst = [doc["corpus_name"] for doc in results.docs]

        return corpus_lst, sc

    def get_corpus_coll_fields(self, corpus_col: str) -> list:
        """Returns a list of the fields of the corpus collection given by 'corpus_col' that have been defined in the Solr server.

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection whose fields are to be retrieved.

        Returns
        -------
        models: list
            List of fields of the corpus collection
        sc: int
            Status code of the request
        """
        sc, results = self.execute_query(q='corpus_name:"'+corpus_col+'"',
                                         col_name=self.corpus_col,
                                         fl="fields")

        if sc != 200:
            self.logger.error(
                f"-- -- Error getting fields of {corpus_col}. Aborting operation...")
            return

        return results.docs[0]["fields"], sc

    def get_corpus_models(self, corpus_col: str):
        """Returns a list with the models associated with the corpus given by 'corpus_col'

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection whose models are to be retrieved.

        Returns
        -------
        models: list
            List of models associated with the corpus
        sc: int
            Status code of the request
        """

        sc, results = self.execute_query(q='corpus_name:"'+corpus_col+'"',
                                         col_name=self.corpus_col,
                                         fl="models")

        if sc != 200:
            self.logger.error(
                f"-- -- Error getting models of {corpus_col}. Aborting operation...")
            return

        return results.docs[0]["models"], sc

    def delete_corpus(self,
                      corpus_logical_path: str):
        """Given the string path of corpus file, it deletes the Solr collection associated with it. Additionally, it removes the document entry of the corpus in the self.corpus_col collection and all the models that have been trained with such a logical corpus.

        Parameters
        ----------
        corpus_logical_path : str
            The path of the logical corpus file to be indexed.
        """

        # 1. Get stem of the logical corpus
        corpus_logical_name = pathlib.Path(corpus_logical_path).stem

        # 2. Delete corpus collection
        _, sc = self.delete_collection(col_name=corpus_logical_name)
        if sc != 200:
            self.logger.error(
                f"-- -- Error deleting corpus collection {corpus_logical_name}")
            return

        # 3. Get ID and associated models of corpus collection in self.corpus_col
        sc, results = self.execute_query(q='corpus_name:'+corpus_logical_name,
                                         col_name=self.corpus_col,
                                         fl="id,models")
        if sc != 200:
            self.logger.error(
                f"-- -- Error getting corpus ID. Aborting operation...")
            return

        # 4. Delete all models associated with the corpus
        for model in results.docs[0]["models"]:
            _, sc = self.delete_collection(col_name=model)
            if sc != 200:
                self.logger.error(
                    f"-- -- Error deleting model collection {model}")
                return

        # 5. Remove corpus from self.corpus_col
        sc = self.delete_doc_by_id(
            col_name=self.corpus_col, id=results.docs[0]["id"])
        if sc != 200:
            self.logger.error(
                f"-- -- Error deleting corpus from {self.corpus_col}")
        return

    # ======================================================
    # MODEL-RELATED OPERATIONS
    # ======================================================
    def index_model(self, model_path: str):
        """
        Given the string path of a model created with the ITMT (i.e., the name of one of the folders representing a model within the TMmodels folder), it extracts the model information and that of the corpus used for its generation. It then adds a new field in the corpus collection of type 'VectorField' and name 'doctpc_{model_name}, and index the document-topic proportions in it. At last, it index the rest of the model information in the model collection.

        Parameters
        ----------
        model_path : str
            Path to the folder of the model to be indexed.
        """

        # 1. Get stem of the model folder
        model_to_index = pathlib.Path(model_path)
        model_name = pathlib.Path(model_to_index).stem

        # 2. Create collection
        _, err = self.create_collection(col_name=model_name)
        if err == 409:
            self.logger.info(
                f"-- -- Collection {model_name} already exists.")
            return
        else:
            self.logger.info(
                f"-- -- Collection {model_name} successfully created.")

        # 3. Create Model object and extract info from the corpus to index
        model = Model(model_to_index)
        json_docs, corpus_name = model.get_model_info_update(action='set')
        sc, results = self.execute_query(q='corpus_name:'+corpus_name,
                                         col_name=self.corpus_col,
                                         fl="id")
        if sc != 200:
            self.logger.error(
                f"-- -- Corpus collection not found in {self.corpus_col}")
            return
        field_update = model.get_corpora_model_update(
            id=results.docs[0]["id"], action='add')

        # 4. Add field for the doc-tpc distribution associated with the model being indexed in the document associated with the corpus
        self.logger.info(
            f"-- -- Indexing model information of {model_name} in {self.corpus_col} starts.")
        self.index_documents(field_update, self.corpus_col, self.batch_size)
        self.logger.info(
            f"-- -- Indexing of model information of {model_name} info in {self.corpus_col} completed.")

        # 5. Modify schema in corpus collection to add field for the doc-tpc distribution associated with the model being indexed
        model_key = 'doctpc_' + model_name
        self.logger.info(
            f"-- -- Adding field {model_key} in {corpus_name} collection")
        _, err = self.add_field_to_schema(
            col_name=corpus_name, field_name=model_key, field_type='VectorField')

        # 6. Index doc-tpc information in corpus collection
        self.logger.info(
            f"-- -- Indexing model information in {corpus_name} collection")
        self.index_documents(json_docs, corpus_name, self.batch_size)

        self.logger.info(
            f"-- -- Indexing model information in {model_name} collection")
        json_tpcs = model.get_model_info()
        self.index_documents(json_tpcs, model_name, self.batch_size)

    def list_model_collections(self) -> list:
        """Returns a list of the names of the model collections that have been created in the Solr server.
        """
        sc, results = self.execute_query(q='*:*',
                                         col_name=self.corpus_col,
                                         fl="models")
        if sc != 200:
            self.logger.error(
                f"-- -- Error getting corpus collections in {self.corpus_col}. Aborting operation...")
            return

        models_lst = [model for doc in results.docs for model in doc["models"]]

        return models_lst, sc

    def delete_model(self, model_path: str):
        """
        Given the string path of a model created with the ITMT (i.e., the name of one of the folders representing a model within the TMmodels folder), 
        it deletes the model collection associated with it. Additionally, it removes the document-topic proportions field in the corpus collection and removes the fields associated with the model and the model from the list of models in the corpus document from the self.corpus_col collection.

        Parameters
        ----------
        model_path : str
            Path to the folder of the model to be indexed.
        """

        # 1. Get stem of the model folder
        model_to_index = pathlib.Path(model_path)
        model_name = pathlib.Path(model_to_index).stem

        # 2. Delete model collection
        _, sc = self.delete_collection(col_name=model_name)
        if sc != 200:
            self.logger.error(
                f"-- -- Error occurred while deleting model collection {model_name}. Stopping...")
            return
        else:
            self.logger.info(
                f"-- -- Model collection {model_name} successfully deleted.")

        # 3. Create Model object and extract info from the corpus associated with the model
        model = Model(model_to_index)
        json_docs, corpus_name = model.get_model_info_update(action='remove')
        sc, results = self.execute_query(q='corpus_name:'+corpus_name,
                                         col_name=self.corpus_col,
                                         fl="id")
        if sc != 200:
            self.logger.error(
                f"-- -- Corpus collection not found in {self.corpus_col}")
            return
        field_update = model.get_corpora_model_update(
            id=results.docs[0]["id"], action='remove')

        # 4. Remove field for the doc-tpc distribution associated with the model being deleted in the document associated with the corpus
        self.logger.info(
            f"-- -- Deleting model information of {model_name} in {self.corpus_col} starts.")
        self.index_documents(field_update, self.corpus_col, self.batch_size)
        self.logger.info(
            f"-- -- Deleting model information of {model_name} info in {self.corpus_col} completed.")

        # 5. Delete doc-tpc information from corpus collection
        self.logger.info(
            f"-- -- Deleting model information from {corpus_name} collection")
        self.index_documents(json_docs, corpus_name, self.batch_size)

        # 6. Modify schema in corpus collection to delete field for the doc-tpc distribution associated with the model being indexed
        model_key = 'doctpc_' + model_name
        self.logger.info(
            f"-- -- Deleting field {model_key} in {corpus_name} collection")
        _, err = self.delete_field_from_schema(
            col_name=corpus_name, field_name=model_key)

        return

    # ======================================================
    # QUERIES
    # ======================================================
    def do_Q1(self,
              corpus_col: str,
              doc_id: str,
              model_name: str):
        """Executes query Q1.

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection.
        id : str
            ID of the document to be retrieved.
        model_name : str
            Name of the model to be used for the retrieval.

        Returns
        -------
        thetas: dict
            JSON object with the document-topic proportions (thetas)
        sc : int
            The status code of the response.  
        """

        # 1. Check that corpus_col is indeed a corpus collection
        corpus_colls, sc = self.list_corpus_collections()
        if corpus_col not in corpus_colls:
            self.logger.error(
                f"-- -- {corpus_col} is not a corpus collection. Aborting operation...")
            return

        # 2. Check that corpus_col has the model_name field
        corpus_fields, sc = self.get_corpus_coll_fields(corpus_col)
        if 'doctpc_' + model_name not in corpus_fields:
            self.logger.error(
                f"-- -- {corpus_col} does not have the field doctpc_{model_name}. Aborting operation...")
            return

        # 3. Execute query
        q1 = self.querier.customize_Q1(id=doc_id, model_name=model_name)
        params = {k: v for k, v in q1.items() if k != 'q'}

        sc, results = self.execute_query(
            q=q1['q'], col_name=corpus_col, **params)

        if sc != 200:
            self.logger.error(
                f"-- -- Error executing query Q1. Aborting operation...")
            return

        return {'thetas': results.docs[0]['doctpc_' + model_name]}, sc

    def do_Q2(self):
        return

    def do_Q3(self, col: str):
        """Executes query Q3.

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection

        Returns
        -------
        nr_docs : int
            Number of documents in the collection
        sc : int
            The status code of the response
        """

        q3 = self.querier.customize_Q3()
        params = {k: v for k, v in q3.items() if k != 'q'}

        sc, results = self.execute_query(
            q=q3['q'], col_name=col, **params)

        if sc != 200:
            self.logger.error(
                f"-- -- Error executing query Q2. Aborting operation...")
            return

        return {'ndocs': int(results.hits)}, sc

    def do_Q4(self,
              corpus_col: str,
              model_name: str,
              topic_id: str,
              thr: str,
              start: str,
              rows: str):
        """Executes query Q4.

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection
        model_name: str
            Name of the model to be used for the retrieval
        topic_id: str
            ID of the topic to be retrieved
        thr: str
            Threshold to be used for the retrieval
        start: str
            Offset into the responses at which Solr should begin displaying content
        rows: str
            How many rows of responses are displayed at a time 

        Returns
        -------
        json_object: dict
            JSON object with the results of the query.
        sc : int
            The status code of the response.  
        """

        # 1. Check that corpus_col is indeed a corpus collection
        corpus_colls, sc = self.list_corpus_collections()
        if corpus_col not in corpus_colls:
            self.logger.error(
                f"-- -- {corpus_col} is not a corpus collection. Aborting operation...")
            return

        # 2. Check that corpus_col has the model_name field
        corpus_fields, sc = self.get_corpus_coll_fields(corpus_col)
        if 'doctpc_' + model_name not in corpus_fields:
            self.logger.error(
                f"-- -- {corpus_col} does not have the field doctpc_{model_name}. Aborting operation...")
            return

        # 3. Customize start and rows
        if start is None:
            start = str(0)
        if rows is None:
            numFound_dict, sc = self.do_Q3(corpus_col)
            rows = str(numFound_dict['ndocs'])

        # 4. Execute query
        q4 = self.querier.customize_Q4(
            model_name=model_name, topic=topic_id, threshold=thr, start=start, rows=rows)
        params = {k: v for k, v in q4.items() if k != 'q'}

        sc, results = self.execute_query(
            q=q4['q'], col_name=corpus_col, **params)

        if sc != 200:
            self.logger.error(
                f"-- -- Error executing query Q3. Aborting operation...")
            return

        return results.docs, sc

    def do_Q5(self,
              corpus_col: str,
              model_name: str,
              doc_id: str,
              start: str,
              rows: str):
        """Executes query Q5.

        Parameters
        ----------
        corpus_col : str
            Name of the corpus collection
        model_name: str
            Name of the model to be used for the retrieval
        doc_id: str
            ID of the document whose similarity is going to be checked against all other documents in 'corpus_col'
         start: str
            Offset into the responses at which Solr should begin displaying content
        rows: str
            How many rows of responses are displayed at a time 

        Returns
        -------
        json_object: dict
            JSON object with the results of the query.
        sc : int
            The status code of the response.  
        """

        # 1. Check that corpus_col is indeed a corpus collection
        corpus_colls, sc = self.list_corpus_collections()
        if corpus_col not in corpus_colls:
            self.logger.error(
                f"-- -- {corpus_col} is not a corpus collection. Aborting operation...")
            return

        # 2. Check that corpus_col has the model_name field
        corpus_fields, sc = self.get_corpus_coll_fields(corpus_col)
        if 'doctpc_' + model_name not in corpus_fields:
            self.logger.error(
                f"-- -- {corpus_col} does not have the field doctpc_{model_name}. Aborting operation...")
            return

        # 3. Execute Q1 to get thetas of document given by doc_id
        thetas_dict, sc = self.do_Q1(
            corpus_col=corpus_col, model_name=model_name, doc_id=doc_id)
        thetas = thetas_dict['thetas']
        thetas_query = ','.join([el.split("|")[1] for el in thetas.split()])

        # 4. Customize start and rows
        if start is None:
            start = str(0)
        if rows is None:
            numFound_dict, sc = self.do_Q3(corpus_col)
            rows = str(numFound_dict['ndocs'])

        # 5. Execute query
        q5 = self.querier.customize_Q5(
            model_name=model_name, thetas=thetas_query,
            start=start, rows=rows)
        params = {k: v for k, v in q5.items() if k != 'q'}

        sc, results = self.execute_query(
            q=q5['q'], col_name=corpus_col, **params)

        if sc != 200:
            self.logger.error(
                f"-- -- Error executing query Q4. Aborting operation...")
            return

        return results.docs, sc
