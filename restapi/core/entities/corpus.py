import json
import pathlib

import dask.dataframe as dd
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
            self._logical_corpus = json.load(fin)

    def get_docs_raw_info(self) -> list[dict]:
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
            df["source"] = DtSet["source"]

            # Rename id-field to id
            df = df.rename(
                columns={idfld: "id"})

        with ProgressBar():
            ddf = df.compute(scheduler='processes')

        json_str = ddf.to_json(orient='records')
        json_lst = json.loads(json_str)

        # rebuild the dictionary for each row, only including non-null values
        # json_lst = [
        #     OrderedDict([
        #         (key, row[key]) for key in ddf.columns
        #         if (key in row) and row[key] is not None or (isinstance(row[key], float) and not math.isnan(row[key]))
        #     ])
        #     for row in json_lst
        # ]

        # with open('/Users/lbartolome/Documents/GitHub/EWB/data/results.json', 'w') as fout:
        #    json.dump(json_lst, fout)

        return json_lst


# if __name__ == '__main__':
#     corpus = Corpus("/Users/lbartolome/Documents/GitHub/EWB/data/Cordis.json")
#     json_lst = corpus.get_docs_raw_info()
#     print(json_lst[0].keys())
