"""
This module is a class implementation to manage and hold all the information associated with a TMmodel. It provides methods to retrieve information about the model such as topic distribution over documents, topic-word probabilities, and betas. 

Note:
-----
This module assumes that the topic model has been trained using the TMmodel class from the same package.

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

import json
import os
import pathlib
import random

import numpy as np
import pandas as pd
import scipy.sparse as sparse
from core.entities.tm_model import TMmodel
from typing import List


class Model(object):
    """
    A class to manage and hold all the information associated with a TMmodel.
    """

    def __init__(self,
                 path_to_model: pathlib.Path,
                 logger=None) -> None:
        """Init method.

        Parameters
        ----------
        path_to_model: pathlib.Path
            Path to the TMmodel folder.
        logger : logging.Logger
            The logger object to log messages and errors.
        """

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Model')

        if not os.path.isdir(path_to_model):
            self._logger.error(
                '-- -- The provided model path does not exist.')
        self.path_to_model = path_to_model

        self.name = path_to_model.stem
        self.corpus_name = None

    @staticmethod
    def sum_up_to(vector: np.ndarray, max_sum: int) -> np.ndarray:
        """It takes in a vector and a max_sum value and returns a NumPy array with the same shape as vector but with the values adjusted such that their sum is equal to max_sum.

        Parameters
        ----------
        vector: 
            The vector to be adjusted.
        max_sum: int
            Number representing the maximum sum of the vector elements.

        Returns:
        --------
        x: 
            A NumPy array of the same shape as vector but with the values adjusted such that their sum is equal to max_sum.
        """
        x = np.array(list(map(np.int_, vector*max_sum))).ravel()
        pos_idx = list(np.where(x != 0)[0])
        while np.sum(x) != max_sum:
            idx = random.choice(pos_idx)
            x[idx] += 1
        return x

    def get_model_info(self) -> List[dict]:
        """It retrieves the information about a topic model and returns it as a list of dictionaries.

        Returns:
        --------
        json_lst: list[dict]
            A list of dictionaries containing information about the topic model.
        """

        # read tr config
        tr_config = self.path_to_model.joinpath("trainconfig.json")
        with pathlib.Path(tr_config).open('r', encoding='utf8') as fin:
            tr_config = json.load(fin)

        tmmodel = TMmodel(self.path_to_model.joinpath("TMmodel"))
        df, vocab_id2w = tmmodel.to_dataframe()
        df = df.apply(pd.Series.explode)
        df.reset_index(drop=True)
        df["id"] = [f"t{i}" for i in range(len(df))]
        # TODO: This should be removed once the topic model makes it on its own
        df["tpc_labels"] = [f"Topic {i}" for i in range(len(df))]
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        df = df[cols]

        # Get betas string representation
        def get_tp_str_rpr(vector, max_sum, vocab_id2w):
            vector = Model.sum_up_to(vector, max_sum)
            rpr = ""
            for idx, val in enumerate(vector):
                if val != 0:
                    rpr += vocab_id2w[str(idx)] + "|" + str(val) + " "
            rpr = rpr.rstrip()
            return rpr

        df["betas"] = df["betas"].apply(
            lambda x: get_tp_str_rpr(x, 1000, vocab_id2w))

        json_str = df.to_json(orient='records')
        json_lst = json.loads(json_str)

        return json_lst

    def get_model_info_update(self, action: str):
        """
        Retrieves the information from the model that goes to a corpus collection (document-topic proportions) and save it as an update in the format required by Solr.

        Parameters
        ----------
        action: str
            Action to be performed ('set', 'remove')

        Returns:
        --------
        json_lst: list[dict]
            A list of dictionaries with thr document-topic proportions update.
        """

        path_to_model = self.path_to_model

        # Read tr configuration
        tr_config = path_to_model.joinpath("trainconfig.json")
        with pathlib.Path(tr_config).open('r', encoding='utf8') as fin:
            tr_config = json.load(fin)

        self.corpus_name = tr_config["TrDtSet"].split("/")[-1].split(".")[0].title()

        thetas = sparse.load_npz(
            path_to_model.joinpath('TMmodel/thetas.npz'))
        thetas_dense = thetas.todense()

        # Get ids of documents kept in the tr corpus
        if tr_config["trainer"] == "mallet":
            ids_corpus = [line.rsplit(' 0 ')[0].strip() for line in open(
                path_to_model.joinpath("corpus.txt"), encoding="utf-8").readlines()]
        elif tr_config["trainer"] == "prodlda" or tr_config["trainer"] == "ctm":
            print("TODO")
            # TODO: Implement for neural models

        # Get doc-topic representation
        def get_doc_str_rpr(vector, max_sum):
            vector = Model.sum_up_to(vector, max_sum)
            rpr = ""
            for idx, val in enumerate(vector):
                if val != 0:
                    rpr += "t" + str(idx) + "|" + str(val) + " "
            rpr = rpr.rstrip()
            return rpr

        doc_tpc_rpr = [get_doc_str_rpr(thetas_dense[row, :], 1000)
                       for row in range(len(thetas_dense))]

        model_key = 'doctpc_' + self.name
        df = pd.DataFrame(list(zip(ids_corpus, doc_tpc_rpr)),
                          columns=['id', model_key])

        json_str = df.to_json(orient='records')
        json_lst = json.loads(json_str)

        new_list = []
        if action == 'set':
            for d in json_lst:
                tpc_dict = {'set': d[model_key]}
                d[model_key] = tpc_dict
                new_list.append(d)
        elif action == 'remove':
            for d in json_lst:
                tpc_dict = {'set': []}
                d[model_key] = tpc_dict
                new_list.append(d)

        return new_list, self.corpus_name

    def get_corpora_model_update(self, id: int, action: str) -> List[dict]:
        """Generates an update for the CORPUS_COL collection.
        Parameters
        ----------
        id: int
            Identifier of the corpus collection in CORPUS_COL
        action: str
            Action to be performed ('add', 'remove')

        Returns:
        --------
        json_lst: list[dict]
            A list of dictionaries with the update.
        """

        json_lst = [{"id": id,
                    "fields": {action: 'doctpc_' + self.name},
                     "models": {action: self.name}
                     }]

        return json_lst


""" if __name__ == '__main__':
    model = Model("/Users/lbartolome/Documents/GitHub/EWB/data/Mallet-25")
    #json_lst = model.get_model_info_update()
    #print(json_lst[0])
    df = model.get_model_info()
    print(df[0].keys())
    upt = model.get_corpora_model_update()
    print(upt) """
