"""
This module ...


Author: Lorena Calvo-Bartolomé
Date: 19/04/2023
"""


class Queries(object):

    def __init__(self) -> None:

        # ================================================================
        # # Q1 ###########################################################
        # # Get document-topic distribution of a selected document in a
        # # corpus collection
        # ================================================================
        self.Q1 = {
            'q': 'id:{}',
            'fl': 'doctpc_{}',
        }

        # Get documents that have a proportion of a certain topic larger than a threshold
        self.Q2 = {

        }

        # Retrieve documents that have a high semantic relationship with a selected document
        # Previous steps:
        # 1. Get thetas of selected documents
        # 2. Parse thetas in Q1
        self.Q3 = {

        }

    def customize_Q1(self, id: str, model_name: str) -> dict:

        custom_q1 = {
            'q': self.Q1['q'].format(id),
            'fl': self.Q1['fl'].format(model_name),
        }
        return custom_q1
