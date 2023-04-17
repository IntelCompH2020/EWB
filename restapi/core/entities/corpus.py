"""
This module is a class implementation to manage and hold all the information associated with a logical corpus.

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

import json
import pathlib

import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from core.entities.utils import convert_datetime_to_strftime, parseTimeINSTANT


class Corpus(object):
    """
    A class to manage and hold all the information associated with a logical corpus.
    """

    def __init__(self,
                 path_to_logical: str,
                 logger=None) -> None:
        """Init method.

        Parameters
        ----------
        path_to_logical: pathlib.Path
            Path the logical corpus json file.
        logger : logging.Logger
            The logger object to log messages and errors.
        """

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Corpus')

        with path_to_logical.open('r', encoding='utf8') as fin:
            self._logical_corpus = json.load(fin)

        self.name = path_to_logical.stem
        self.fields = None

    def get_docs_raw_info(self) -> list[dict]:
        """Extracts the information contained in the parquet file associated to the logical corpus and transforms into a list of dictionaries.

        Returns:
        --------
        json_lst: list[dict]
            A list of dictionaries containing information about the corpus.
        """
        if len(self._logical_corpus['Dtsets']) > 1:
            self._logger.error(
                f"Only models coming from a logical corpus associated with one raw dataset can be processed.")
            return
        else:
            DtSet = self._logical_corpus['Dtsets'][0]
            df = dd.read_parquet(DtSet['parquet']).fillna("")
            idfld = DtSet["idfld"]

            # Concatenate text fields
            for idx2, col in enumerate(DtSet['lemmasfld']):
                if idx2 == 0:
                    df["all_lemmas"] = df[col]
                else:
                    df["all_lemmas"] += " " + df[col]

            # Rename id-field to id
            df = df.rename(
                columns={idfld: "id"})

        with ProgressBar():
            ddf = df.compute(scheduler='processes')

        # Save corpus fields
        self.fields = ddf.columns.tolist()

        # Convert dates information to the format required by Solr ( ISO_INSTANT, The ISO instant formatter that formats or parses an instant in UTC, such as '2011-12-03T10:15:30Z')
        ddf, cols = convert_datetime_to_strftime(ddf)
        ddf[cols] = ddf[cols].applymap(parseTimeINSTANT)

        json_str = ddf.to_json(orient='records')
        json_lst = json.loads(json_str)

        return json_lst

    def get_corpora_update(self, id: int) -> list[dict]:

        fields_dict = [{"id": id,
                        "corpus_name": self.name,
                        "fields": self.fields}]

        return fields_dict

    def calculate_sim_pairs(self):
        # TODO: Pairs of documents with very high semantic similarity.
        pass


# if __name__ == '__main__':
#     corpus = Corpus("/Users/lbartolome/Documents/GitHub/EWB/data/Cordis.json")
#     json_lst = corpus.get_docs_raw_info()
#     import pdb
#     pdb.set_trace()
#     # print(json_lst[0].keys())
