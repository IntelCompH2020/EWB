
import json
import os
import pathlib
import random
import scipy.sparse as sparse
import pandas as pd
import numpy as np

class Model(object):
    def __init__(self, path_to_model: pathlib.Path, logger=None) -> None:

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Model')

        if not os.path.isdir(path_to_model):
            self._logger.error(
                '-- -- The provided model path does not exist.')
        self.path_to_model = pathlib.Path(path_to_model)
        #tmmodel = TMmodel(path_to_tmmodel)
        # self._create_model(tmmodel)

    def _create_model(self, path_to_model):

        # read tr config
        tr_config = path_to_model.joinpath("trainconfig.json")
        with pathlib.Path(tr_config).open('r', encoding='utf8') as fin:
            tr_config = json.load(fin)

        pass
    
    def add_info_tmmodel(self) -> None:
        
        path_to_model = self.path_to_model

        # read tr config
        tr_config = path_to_model.joinpath("trainconfig.json")
        with pathlib.Path(tr_config).open('r', encoding='utf8') as fin:
            tr_config = json.load(fin)

        thetas = sparse.load_npz(
            path_to_model.joinpath('TMmodel/thetas.npz'))
        thetas_dense = thetas.todense()

        # Get ids of documents kept in the tr corpus
        if tr_config["trainer"] == "mallet":
            ids_corpus = [line.rsplit(' 0 ')[0].strip() for line in open(
                path_to_model.joinpath("corpus.txt"), encoding="utf-8").readlines()]
        elif tr_config["trainer"] == "prodlda" or tr_config["trainer"] == "ctm":
            print("TODO")

        # Get doc-topic representation
        def sum_up_to(vector, max_sum):
            x = np.array(list(map(np.int_, vector*max_sum))).ravel()
            pos_idx = list(np.where(x != 0)[0])
            while np.sum(x) != max_sum:
                idx = random.choice(pos_idx)
                x[idx] += 1
            return x

        def get_str_rpr(vector, max_sum):
            vector = sum_up_to(vector, max_sum)
            rpr = ""
            for idx, val in enumerate(vector):
                rpr += "t" + str(idx) + "|" + str(val) + " "
            rpr = rpr.rstrip()
            return rpr

        doc_tpc_rpr = [get_str_rpr(thetas_dense[row, :], 1000)
                       for row in range(len(thetas_dense))]

        df = pd.DataFrame(list(zip(ids_corpus, doc_tpc_rpr)),
                          columns=['id', 'doc-tpc'])
        
        json_str = df.to_json(orient='records')
        json_lst = json.loads(json_str)
        
        new_list = []
        for d in json_lst:
            tpc_dict = { 'set': d['doc-tpc'] }
            d['doc-tpc'] = tpc_dict
            new_list.append(d)

        return new_list

# if __name__ == '__main__':
#     model = Model("/Users/lbartolome/Documents/GitHub/EWB/data/Mallet-25")
#     json_lst = model.add_info_tmmodel()
#     print(json_lst[0:2])
    
