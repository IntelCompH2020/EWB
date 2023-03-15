import os
import requests

BATCH_SIZE = 100


class SolrResp:
    def __init__(self, resp, logger):
        resp = resp.json()
        self.status_code = 400
        if 'responseHeader' in resp and resp['responseHeader']['status'] == 0:
            logger.info('-- -- Request acknowledged')
            self.status_code = 200
        else:
            self.status_code = resp['responseHeader']['status']
            self.text = resp['error']['msg']
            logger.error(
                f'-- -- Request generated an error {self.status_code}: {self.text}')


class SolrClient():
    def __init__(self, logger):
        self.solr_url = os.environ.get('SOLR_URL')
        self.solr = requests.Session()
        self.logger = logger

    @staticmethod
    def resp_msg(msg: str, resp: SolrResp, throw=True):
        print('resp_msg: {} [Status: {}]'.format(msg, resp.status_code))
        if resp.status_code >= 400:
            print(resp.text)
            if throw:
                raise RuntimeError(resp.text)

    def create_collection(self, col_name: str, config: str = 'ewb_config', nshards: int = 1, replicationFactor: int = 1):

        headers_ = {"Content-Type": "application/json"}
        data = {
            "create": {
                "name": col_name,
                "config": config,
                "numShards": nshards,
                "replicationFactor": replicationFactor
            }
        }
        resp = requests.post(
            url='{}/api/collections?'.format(self.solr_url), headers=headers_, json=data, timeout=10)

        self.resp_msg(
            "Created collection {}".format(col_name), SolrResp(resp, self.logger))

        return

    # def index_documents(documents_filename, embedding_filename):
    #     # Open the file containing text.
    #     with open(documents_filename, "r") as documents_file:
    #         # Open the file containing vectors.
    #         with open(embedding_filename, "r") as vectors_file:
    #             documents = []
    #             # For each document creates a JSON document including
    #             both text and related vector.
    #             for index, (document, vector_string) in enumerate
    #             (zip(documents_file, vectors_file)):

    #                 vector =
    #                 [float(w) for w in vector_string.split(",")]
    #                 doc = {
    #                     "id": str(index),
    #                     "text": document,
    #                     "vector": vector
    #                 }
    #                 # Append JSON document to a list.
    #                 documents.append(doc)

    #                 # To index batches of documents at a time.
    #                 if index % BATCH_SIZE == 0 and index != 0:
    #                     # How you'd index data to Solr.
    #                     solr.add(documents)
    #                     documents = []
    #                     print("==== indexed {} documents ======"
    #                     .format(index))
    #             # To index the rest, when 'documents' list < BATCH_SIZE.
    #             if documents:
    #                 solr.add(documents)
    #             print("finished")

    ############################################################################

    def delete_index(self, index):
        params = {
            'action': 'UNLOAD',
            'core': index,
            'deleteIndex': 'true',
            'deleteDataDir': 'true',
            'deleteInstanceDir': 'true'
        }

        resp = requests.get(
            '{}/admin/cores?'.format(self.solr_base_ep), params=params)
        self.resp_msg("Deleted index {}".format(index), SolrResp(resp))

    def create_index(self, index_name, index_spec):
        # Presumes there is a link between the docker container and the 'index'
        # directory under docker/solr/ (ie docker/solr/tmdb/ is linked into
        # Docker container configsets)
        params = {
            'action': 'CREATE',
            'name': index_name,
            'configSet': index_spec,
        }
        resp = requests.get(
            '{}/admin/cores?'.format(self.solr_base_ep), params=params)

        self.resp_msg("Created index {}".format(index_name), SolrResp(resp))

    def index_documents(self, index, doc_src):
        def commit():
            print('Committing changes')
            resp = requests.get(
                '{}/{}/update?commit=true'.format(self.solr_base_ep, index))
            self.resp_msg("Committed index {}".format(index), resp)

        def flush(docs):
            print('Flushing {} docs'.format(len(docs)))
            resp = requests.post('{}/{}/update'.format(
                self.solr_base_ep, index), json=docs)
            self.resp_msg("Done", resp)
            docs.clear()

        BATCH_SIZE = 5000
        docs = []
        for doc in doc_src:
            if 'release_date' in doc and doc['release_date'] is not None:
                doc['release_date'] += 'T00:00:00Z'

            docs.append(doc)

            if len(docs) % BATCH_SIZE == 0:
                flush(docs)

        flush(docs)
        commit()

    def query(self, index, query):
        url = '{}/{}/select?'.format(self.solr_base_ep, index)

        resp = requests.post(url, data=query)
        #resp_msg(msg='Query {}...'.format(str(query)[:20]), resp=resp)
        resp = resp.json()

        qtime = resp['responseHeader']['QTime']
        numfound = resp['response']['numFound']

        return resp['response']['docs'], qtime, numfound

    def analyze(self, index, fieldtype, text):
        # http://localhost:8983/solr/msmarco/analysis/field
        url = '{}/{}/analysis/field?'.format(self.solr_base_ep, index)

        query = {
            "analysis.fieldtype": fieldtype,
            "analysis.fieldvalue": text
        }

        resp = requests.post(url, data=query)

        analysis_resp = resp.json()
        tok_stream = analysis_resp['analysis']['field_types']['text_general']['index']
        tok_stream_result = tok_stream[-1]
        return tok_stream_result

    def term_vectors_skip_to(self, index, q='*:*', skip=0):
        url = '{}/{}/tvrh/'.format(self.solr_base_ep, index)
        query = {
            'q': q,
            'cursorMark': '*',
            'sort': 'id asc',
            'fl': 'id',
            'rows': str(skip)
        }
        tvrh_resp = requests.post(url, data=query)
        return tvrh_resp.json()['nextCursorMark']

    def get_doc(self, index, doc_id):
        params = {
            'q': 'id:{}'.format(doc_id),
            'wt': 'json'
        }

        resp = requests.post(
            '{}/{}/select'.format(self.solr_base_ep, index), data=params).json()
        return resp['response']['docs'][0]
