"""
This module defines a class with the EWB-specific queries used to interact with Solr.


Author: Lorena Calvo-Bartolomé
Date: 19/04/2023
"""


class Queries(object):

    def __init__(self) -> None:

        # ================================================================
        # # Q1: getThetasDocById  ##################################################################
        # # Get document-topic distribution of a selected document in a
        # # corpus collection
        # http://localhost:8983/solr/{col}/select?fl=doctpc_{model}&q=id:{id}
        # ================================================================
        self.Q1 = {
            'q': 'id:{}',
            'fl': 'doctpc_{}',
        }

        # ================================================================
        # # Q2: getMetadataDocById  ##################################################################
        # # Get metadata of a selected document in a corpus collection
        # ================================================================
        self.Q2 = {
            'q': 'id:{}',
            'fl': '',
        }

        # ================================================================
        # # Q3: getNrDocsColl ##################################################################
        # # Get number of documents in a collection
        # http://localhost:8983/solr/{col}/select?q=*:*&wt=json&rows=0
        # ================================================================
        self.Q3 = {
            'q': '*:*',
            'rows': '0',
        }

        # ================================================================
        # # Q4: GetDocsWithThetasLargerThanThr ##################################################################
        # # Get documents that have a proportion of a certain topic larger
        # # than a threshold
        # q={!payload_check f=doctpc_{tpc} payloads="{thr}" op="gte"}t{tpc}
        # ================================================================
        self.Q4 = {
            'q': "{{!payload_check f=doctpc_{} payloads='{}' op='gte'}}t{}",
            'start': '{}',
            'rows': '{}',
            'fl': "id,doctpc_{}"
        }

        # ================================================================
        # # Q5: getDocsWithHighSimWithDocByid
        # ################################################################
        # # Retrieve documents that have a high semantic relationship with
        # # a selected document
        # q={!payload_check f=doctpc_Mallet-25 payloads="5" op="gte"}t5
        # ---------------------------------------------------------------
        # Previous steps:
        # ---------------------------------------------------------------
        # 1. Get thetas of selected documents
        # 2. Parse thetas in Q1
        # 3. Execute Q4
        # ================================================================
        self.Q5 = {
            'q': "{{!vp f=doctpc_{} vector=\"{}\"}}",
            'fl': "id,score",
            'start': '{}',
            'rows': '{}'
        }

    def customize_Q1(self, id: str, model_name: str) -> dict:
        """Customizes query Q1 'getThetasDocById'.

        id: str
            Document id.
        model_name: str
            Name of the topic model whose topic distribution is to be retrieved.
        """

        custom_q1 = {
            'q': self.Q1['q'].format(id),
            'fl': self.Q1['fl'].format(model_name),
        }
        return custom_q1

    def customize_Q2(self) -> dict:

        return self.Q2

    def customize_Q3(self) -> dict:

        return self.Q3

    def customize_Q4(self,
                     model_name: str,
                     topic: str,
                     threshold: str,
                     start: str,
                     rows: str) -> dict:

        custom_q4 = {
            'q': self.Q4['q'].format(model_name, str(threshold), str(topic)),
            'start': self.Q4['start'].format(start),
            'rows': self.Q4['rows'].format(rows),
        }
        return custom_q4

    def customize_Q5(self, model_name: str,
                     thetas: str,
                     start: str,
                     rows: str) -> dict:

        custom_q5 = {
            'q': self.Q5['q'].format(model_name, thetas),
            'fl': self.Q5['fl'].fornat(model_name),
            'start': self.Q5['start'].format(start),
            'rows': self.Q5['rows'].format(rows),
        }
        return custom_q5
