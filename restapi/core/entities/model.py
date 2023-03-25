
import pathlib
import numpy as np
import os

from restapi.core.entities.tm_model import TMmodel

class Model(object):
    def __init__(self, path_to_tmmodel: pathlib.Path, logger = None) -> None:

        if logger:
            self._logger = logger
        else:
            import logging
            logging.basicConfig(level='INFO')
            self._logger = logging.getLogger('Entity Model')
            
        if not os.path.isdir(path_to_tmmodel):
            self._logger.error(
                '-- -- The provided TMmodel path does not exist.')
        tmmodel = TMmodel(path_to_tmmodel)
        self._create_model(tmmodel)
        
        
    def _create_model(self, tmmodel):
        pass