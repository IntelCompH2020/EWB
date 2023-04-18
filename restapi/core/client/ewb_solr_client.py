"""
This module provides a specific class for handeling the Solr API responses and requests of the EWB.

Author: Lorena Calvo-Bartolomé
Date: 17/04/2023
"""

import logging
import pathlib
import configparser
from core.entities.corpus import Corpus
from core.entities.model import Model

from core.client.base.solr_client import SolrClient


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
            self.logger.info(sc)
            self.logger.info(type(sc))
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

        self.logger.info("this is the id")
        self.logger.info(results.docs[0]["id"])
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
        model_name : str
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
        json_docs, corpus_name = model.get_model_info_update()
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
            f"-- -- Indexing model inforamtion of {model_name} in {self.corpus_col} starts.")
        self.index_documents(field_update, self.corpus_col, self.batch_size)
        self.logger.info(
            f"-- -- Indexing of model inforamtion of {model_name} info in {self.corpus_col} completed.")

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

    def delete_model(self, model_name: str):

        # 1. Create Model object
        model_to_delete = "/data/source/" + model_name
        model = Model(model_to_delete)

        # 2. Delete model collection
        _, sc = self.delete_collection(col_name=model_name)

        # 2. Generate update with get_corpora_model_update & delete to delete tpc-distric field in field and model from models in corpus collection within CORPUS_COL

        # 3. Generate update with get_model_info_update & delete (add the field to action:str to be customizable btwn set and delete) to remove model infromation from corpus collection

        return