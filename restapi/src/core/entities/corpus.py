"""
This module is a class implementation to manage and hold all the information associated with a logical corpus.

Author: Lorena Calvo-Bartolomé
Date: 27/03/2023
"""

import configparser
import json
from typing import List

import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from src.core.entities.utils import (convert_datetime_to_strftime,
                                     parseTimeINSTANT)


class Corpus(object):
    """
    A class to manage and hold all the information associated with a logical corpus.
    """

    def __init__(self,
                 path_to_logical: str,
                 logger=None,
                 config_file: str = "/config/config.cf") -> None:
        """Init method.

        Parameters
        ----------
        path_to_logical: pathlib.Path
            Path the logical corpus json file.
        logger : logging.Logger
            The logger object to log messages and errors.
        config_file: str
            Path to the configuration file.
        """

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Corpus')

        with path_to_logical.open('r', encoding='utf8') as fin:
            self._logical_corpus = json.load(fin)

        self.name = path_to_logical.stem.lower()
        self.fields = None

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self._logger.info(f"Sections {cf.sections()}")
        if self.name + "-config" in cf.sections():
            section = self.name + "-config"
        elif path_to_logical.stem + "-config" in cf.sections():
            section = path_to_logical.stem + "-config"
        else:
            self._logger.error(
                f"Logical corpus configuration {self.name} not found in config file.")
        self.title_field = cf.get(section, "title_field")
        self.date_field = cf.get(section, "date_field")
        
        return

    def get_docs_raw_info(self) -> List[dict]:
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
            ddf = dd.read_parquet(DtSet['parquet']).fillna("")
            idfld = DtSet["idfld"]

            # Concatenate text fields
            for idx2, col in enumerate(DtSet['lemmasfld']):
                if idx2 == 0:
                    ddf["all_lemmas"] = ddf[col]
                else:
                    ddf["all_lemmas"] += " " + ddf[col]

            # Rename id-field to id, title-field to title and date-field to date
            ddf = ddf.rename(
                columns={idfld: "id",
                         self.title_field: "title",
                         self.date_field: "date"})

        with ProgressBar():
            df = ddf.compute(scheduler='processes')

        df["nwords_per_doc"] = df["all_lemmas"].apply(lambda x: len(x.split()))

        # Save corpus fields
        self.fields = df.columns.tolist()

        # Convert dates information to the format required by Solr ( ISO_INSTANT, The ISO instant formatter that formats or parses an instant in UTC, such as '2011-12-03T10:15:30Z')
        df, cols = convert_datetime_to_strftime(df)
        df[cols] = df[cols].applymap(parseTimeINSTANT)

        json_str = df.to_json(orient='records')
        json_lst = json.loads(json_str)

        return json_lst

    def get_corpora_update(self, id: int) -> List[dict]:

        fields_dict = [{"id": id,
                        "corpus_name": self.name,
                        "fields": self.fields}]

        return fields_dict


# if __name__ == '__main__':
#     corpus = Corpus("/Users/lbartolome/Documents/GitHub/EWB/data/Cordis.json")
#     json_lst = corpus.get_docs_raw_info()
#     import pdb
#     pdb.set_trace()
#     # print(json_lst[0].keys())
