"""
This module defines a class with the EWB-specific queries used to interact with Solr.


Author: Lorena Calvo-Bartolomé
Date: 19/04/2023
"""


class Queries(object):

    def __init__(self) -> None:

        # ================================================================
        # # Q1 ###########################################################
        # # Get document-topic distribution of a selected document in a
        # # corpus collection
        # http://localhost:8983/solr/{col}/select?fl=doctpc_{model}&q=id:{id}
        # ================================================================
        self.Q1 = {
            'q': 'id:{}',
            'fl': 'doctpc_{}',
        }

        # ================================================================
        # # Q2 ###########################################################
        # # Get number of documents in a collection
        # http://localhost:8983/solr/{col}/select?q=*:*&wt=json&rows=0
        # ================================================================
        self.Q2 = {
            'q': '*:*',
            'rows': '0',
        }

        # ================================================================
        # # Q3 ###########################################################
        # # Get documents that have a proportion of a certain topic larger
        # # than a threshold
        # q={!payload_check f=doctpc_{tpc} payloads="{thr}" op="gte"}t{tpc}
        # ================================================================
        self.Q3 = {
            'q': "{{!payload_check f=doctpc_{} payloads='{}' op='gte'}}t{}",
            'rows': '{}'
        }

        # ================================================================
        # # Q4 ###########################################################
        # # Retrieve documents that have a high semantic relationship with
        # # a selected document
        # ---------------------------------------------------------------
        # Previous steps:
        # ---------------------------------------------------------------
        # 1. Get thetas of selected documents
        # 2. Parse thetas in Q1
        # ================================================================
        self.Q4 = {

        }

    def customize_Q1(self, id: str, model_name: str) -> dict:

        custom_q1 = {
            'q': self.Q1['q'].format(id),
            'fl': self.Q1['fl'].format(model_name),
        }
        return custom_q1

    def customize_Q2(self) -> dict:

        return self.Q2

    def customize_Q3(self, model_name: str, topic: str, threshold: str, rows: int) -> dict:

        custom_q3 = {
            'q': self.Q3['q'].format(model_name, str(threshold), str(topic)),
            'rows': self.Q3['rows'].format(rows),
        }
        return custom_q3
