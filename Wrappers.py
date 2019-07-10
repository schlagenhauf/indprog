
#import matlab.engine

import subprocess
import struct
import codecs
from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

from SecureFileOps import *

##
# @brief Wrapper for the process that a node represents. Can wrap a variety of actions.
class Process(ABC):
    def __init__(self, name):
        self.name = name
        self.portSpecs = [[],[]]

    ##
    # @brief Returns the port specifications of this process so that the containing node
    # can create them
    #
    # @return List of port specifications
    def getPortSpecs(self):
        return self.portSpecs


    def upToDate(self):
        return False

    @abstractmethod
    def run(self, inFds, outFds):
        pass


class DummyProcess(Process):
    def __init__(self,name):
        super(DummyProcess, self).__init__(name)
        self.portSpecs = [['inport'],['outport']]

    def run(self, inData, outData):
        logger.debug('inData: %s' % inData)

        # TODO this does not work, do a deep copy
        outData = inData
