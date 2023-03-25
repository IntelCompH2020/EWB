import json
import math
import pathlib
from collections import OrderedDict

import dask.dataframe as dd
import pandas as pd
from dask.diagnostics import ProgressBar


class Corpus(object):
    def __init__(self,
                 path_to_logical: str,
                 logger=None) -> None:

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Corpus')

        with pathlib.Path(path_to_logical).open('r', encoding='utf8') as fin:
            logical_corpus = json.load(fin)

        # Read all dataset that compose a logical corpus in one df
        for idx, DtSet in enumerate(logical_corpus['Dtsets']):
            df = dd.read_parquet(DtSet['parquet']).fillna("")
            idfld = DtSet["idfld"]

            # Concatenate text fields
            for idx2, col in enumerate(DtSet['lemmasfld']):
                if idx2 == 0:
                    df["all_lemmas"] = df[col]
                else:
                    df["all_lemmas"] += " " + df[col]
            df["source"] = DtSet["source"]

            # Rename id-field to id
            df = df.rename(
                columns={idfld: "id"})

            # Concatenate dataframes
            if idx == 0:
                trDF = df
            else:
                trDF = dd.concat([trDF, df], axis=0, join='outer')

        with ProgressBar():
            ddf = trDF.compute(scheduler='processes')

        json_str = ddf.to_json(orient='records')
        json_lst = json.loads(json_str)

        # rebuild the dictionary for each row, only including non-null values
        json_lst = [
            OrderedDict([
                (key, row[key]) for key in ddf.columns
                if (key in row) and row[key] is not None or (isinstance(row[key], float) and not math.isnan(row[key]))
            ])
            for row in json_lst
        ]

    def add_info_tmmodel(self, path_to_tmmodel: pathlib.Path) -> None:
        pass


if __name__ == '__main__':
    corpus = Corpus("/Users/lbartolome/Documents/GitHub/EWB/test/Cordis.json")
