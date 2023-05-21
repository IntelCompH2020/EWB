
import configparser
import logging
import pathlib
import time
from typing import Union
from src.core.inferencer.base.inferencer import (CTMInferencer,
                                                 MalletInferencer,
                                                 ProdLDAInferencer,
                                                 SparkLDAInferencer)


class EWBMalletInferencer(MalletInferencer):
    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = "/config/config.cf"):
        """
        Initilization Method

        Parameters
        ----------
        logger: Logger object
            To log object activity
        config_file: str
            Path to the config file
        """

        super().__init__(logger)

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self.mallet_path = cf.get('mallet', 'mallet_path')
        self.max_sum = cf.getint('restapi', 'max_sum')

    def predict(self, inferConfigFile: pathlib.Path) -> Union[dict, None]:
        """Execute inference on the given text and returns a response in the format expected by the API.

        Parameters
        ----------
        inferConfigFile: pathlib.Path
            Path to the configuration file for inference

        Returns
        -------
        response: dict
            A dictionary containing the response header and the response, if any, following the API format:
            {
                "responseHeader": {
                    "status": 200 or 400,
                    "time": 0.0
                },  
                "response": {
                    [{'id': 1, thetas: 't1|X1 t2|X1 t3|X3 t4|X4 t5|X5'},
                     {'id': 1, thetas: 't1|X1 t5|X5'},
                     {'id': 1, thetas: 't2|X2 t4|X4 t5|X5'},
                     ...] or None
                }
            }     
        sc: int
            Status code of the response                                               
        """

        start_time = time.time()

        try:
            resp = super().predict(inferConfigFile=inferConfigFile,
                                   mallet_path=self.mallet_path,
                                   max_sum=self.max_sum)
            end_time = time.time() - start_time
            sc = 200
            responseHeader = {"status": sc,
                              "time": end_time}

            response = {"responseHeader": responseHeader,
                        "response": resp}

            self._logger.info(f"-- -- Inference completed successfully")

        except Exception as e:
            end_time = time.time() - start_time
            sc = 400
            responseHeader = {"status": sc,
                              "time": end_time,
                              "error": str(e)}

            response = {"responseHeader": responseHeader,
                        "response": None}

            self._logger.info(
                f"-- -- Inference failed with error: {str(e)}")

        return response, sc


class EWBSparkLDAInferencer(SparkLDAInferencer):
    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = "/config/config.cf"):
        """
        Initilization Method

        Parameters
        ----------
        logger: Logger object
            To log object activity
        config_file: str
            Path to the config file
        """

        super().__init__(logger)

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self.max_sum = cf.getint('restapi', 'max_sum')

    def predict(self, inferConfigFile: pathlib.Path) -> Union[dict, None]:
        # TODO: Implement predict method
        pass


class EWBProdLDAInferencer(ProdLDAInferencer):
    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = "/config/config.cf"):
        """
        Initilization Method

        Parameters
        ----------
        logger: Logger object
            To log object activity
        config_file: str
            Path to the config file
        """

        super().__init__(logger)

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self.max_sum = cf.getint('restapi', 'max_sum')

    def predict(self, inferConfigFile: pathlib.Path) -> Union[dict, None]:
        # TODO: Implement predict method
        pass


class EWBCTMInferencer(CTMInferencer):
    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = "/config/config.cf"):
        """
        Initilization Method

        Parameters
        ----------
        logger: Logger object
            To log object activity
        config_file: str
            Path to the config file
        """

        super().__init__(logger)

        # Read configuration from config file
        cf = configparser.ConfigParser()
        cf.read(config_file)
        self.max_sum = cf.getint('restapi', 'max_sum')

    def predict(self, inferConfigFile: pathlib.Path) -> Union[dict, None]:
        # TODO: Implement predict method
        pass
