import json
import pathlib
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
from datetime import datetime
import pytz
import math


def is_valid_xml_char_ordinal(i):
    """
    Defines whether char is valid to use in xml document
    XML standard defines a valid char as::
    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
    """
    # conditions ordered by presumed frequency
    return (
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
    )


def clean_xml_string(s):
    """
    Cleans string from invalid xml chars
    Solution was found there::
    http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    """
    return "".join(c for c in s if is_valid_xml_char_ordinal(ord(c)))


def convert_datetime_to_strftime(df):
    """
    Converts all columns of type datetime64[ns] in a dataframe to strftime format.
    """
    columns = []
    for column in df.columns:
        if df[column].dtype == "datetime64[ns]":
            columns.append(column)
            df[column] = df[column].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df, columns


def parseTimeINSTANT(time):
    """
    Parses a string representing an instant in time and returns it as an Instant object.
    """
    format_string = '%Y-%m-%d %H:%M:%S'
    if isinstance(time, str) and time != "foo":
        dt = datetime.strptime(time, format_string)
        dt_utc = dt.astimezone(pytz.UTC)
        return clean_xml_string(dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    elif time == "foo":
        return clean_xml_string("")
    else:
        if math.isnan(time):
            return clean_xml_string("")


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

            # Rename id-field to id
            df = df.rename(
                columns={idfld: "id"})

        with ProgressBar():
            ddf = df.compute(scheduler='processes')

        # Convert dates information to the format required by Solr ( ISO_INSTANT, The ISO instant formatter that formats or parses an instant in UTC, such as '2011-12-03T10:15:30Z')

        ddf, cols = convert_datetime_to_strftime(ddf)
        ddf[cols] = ddf[cols].applymap(parseTimeINSTANT)

        json_str = ddf.to_json(orient='records')
        json_lst = json.loads(json_str)

        return json_lst


if __name__ == '__main__':
    corpus = Corpus("/Users/lbartolome/Documents/GitHub/EWB/data/Cordis.json")
    json_lst = corpus.get_docs_raw_info()
    import pdb
    pdb.set_trace()
    # print(json_lst[0].keys())
