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
        # # Q2: getNrDocsColl ##################################################################
        # # Get number of documents in a collection
        # http://localhost:8983/solr/{col}/select?q=*:*&wt=json&rows=0
        # ================================================================
        self.Q2 = {
            'q': '*:*',
            'rows': '0',
        }

        # ================================================================
        # # Q3: GetDocsWithThetasLargerThanThr ##################################################################
        # # Get documents that have a proportion of a certain topic larger
        # # than a threshold
        # q={!payload_check f=doctpc_{tpc} payloads="{thr}" op="gte"}t{tpc}
        # ================================================================
        self.Q3 = {
            'q': "{{!payload_check f=doctpc_{} payloads='{}' op='gte'}}t{}",
            'start': '{}',
            'rows': '{}'
        }

        # ================================================================
        # # Q4: GetDocsWithHighSemanticRelationshipWithDocid
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
        self.Q4 = {
            'q': "{{!vp f=doctpc_{} vector=\"{}\"}}",
            'fl': "id,score",
            'start': '{}',
            'rows': '{}'
        }

        # ================================================================
        # # Q5: GetCorpusDocumentList
        # ################################################################
        # # Get a list with the id of all the documents in a collection
        # ================================================================
        self.Q5 = {
            # TODO: implement this query
        }

        # ================================================================
        # # Q6: GetCorpusDocumentDetails
        # ################################################################
        # # Get a list with the information of all the documents in a
        # collection
        # ================================================================
        self.Q6 = {
            # TODO: implement this query
        }

    def customize_Q1(self, id: str, model_name: str) -> dict:

        custom_q1 = {
            'q': self.Q1['q'].format(id),
            'fl': self.Q1['fl'].format(model_name),
        }
        return custom_q1

    def customize_Q2(self) -> dict:

        return self.Q2

    def customize_Q3(self,
                     model_name: str,
                     topic: str,
                     threshold: str,
                     start: str,
                     rows: str) -> dict:

        custom_q3 = {
            'q': self.Q3['q'].format(model_name, str(threshold), str(topic)),
            'start': self.Q3['start'].format(start),
            'rows': self.Q3['rows'].format(rows),
        }
        return custom_q3

    def customize_Q4(self, model_name: str,
                     thetas: str,
                     start: str,
                     rows: str) -> dict:

        custom_q4 = {
            'q': self.Q4['q'].format(model_name, thetas),
            'fl': self.Q4['fl'],
            'start': self.Q4['start'].format(start),
            'rows': self.Q4['rows'].format(rows),
        }
        return custom_q4
