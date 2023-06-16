"""
This  module provides 2 classes to handle Inferencer API responses and requests.

The InferencerResponse class handles Inferencer API response and errors, while the EWBInferencerClient class handles requests to the Inferencer API.

Author: Lorena Calvo-Bartolomé
Date: 21/05/2023
"""

import logging
import os

import requests


class InferencerResponse(object):
    """
    A class to handle Inferencer API response and errors.
    """

    def __init__(self,
                 resp: requests.Response,
                 logger: logging.Logger) -> None:

        # Get JSON object of the result
        resp = resp.json()

        self.status_code = resp['responseHeader']['status']
        self.time = resp['responseHeader']['time']
        self.results = resp['response']

        if self.status_code == 200:
            logger.info(f"-- -- Inferencer request acknowledged")
        else:
            logger.info(
                f"-- -- Inference request generated an error: {self.results['error']}")
        return


class EWBInferencerClient(object):
    """
    A class to handle EWB Inferencer API requests.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """
        Parameters
        ----------
        logger : logging.Logger
            The logger object to log messages and errors.
        """

        # Get the Inferencer URL from the environment variables
        self.inferencer_url = os.environ.get('INFERENCE_URL')

        # Initialize requests session and logger
        self.inferencer = requests.Session()

        if logger:
            self.logger = logger
        else:
            import logging
            logging.basicConfig(level='DEBUG')
            self.logger = logging.getLogger('Inferencer')
        return

    def _do_request(self,
                    type: str,
                    url: str,
                    timeout: int = None,
                    **params) -> InferencerResponse:
        """Sends a request to the Inferencer API and returns an object of the InferencerResponse class.

        Parameters
        ----------
        type : str
            The type of the request.
        url : str
            The URL of the Inferencer API.
        timeout : int, optional
            The timeout of the request in seconds, by default 10.
        **params: dict
            The parameters of the request.

        Returns
        -------
        InferencerResponse: InferencerResponse
            An object of the InferencerResponse class.
        """

        # Send request
        if type == "get":
            resp = requests.get(
                url=url,
                timeout=timeout,
                **params
            )
            pass
        elif type == "post":
            resp = requests.post(
                url=url,
                timeout=timeout,
                **params
            )
        else:
            self.logger.error(f"-- -- Invalid type {type}")
            return

        # Parse Inference response
        inf_resp = InferencerResponse(resp, self.logger)

        return inf_resp

    def infer_doc(self,
                  text_to_infer: str,
                  model_for_inference: str) -> InferencerResponse:
        """Execute inference on the given text and returns a response in the format expected by the API.

        Parameters
        ----------
        text_to_infer : str
            The text to infer.
        model_for_inference : str
            The model to use for inference.

        Returns
        -------
        InferencerResponse: InferencerResponse
            An object of the InferencerResponse class.
        """

        headers_ = {'Accept': 'application/json'}

        params_ = {
            'text_to_infer': text_to_infer,
            'model_for_infer': model_for_inference
        }

        url_ = '{}/inference_operations/inferDoc'.format(self.inferencer_url)

        # Send request to Inferencer
        inf_resp = self._do_request(
            type="post", url=url_, headers=headers_, params=params_)

        return inf_resp

    def infer_corpus(self,
                     corpus_to_infer: str,
                     model_for_inference: str):
        # TODO: Implement this method
        pass
