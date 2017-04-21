import os
import struct
from abc import ABC, abstractmethod
import uuid
import tempfile
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from Wrappers import *

class ProcessingGraph:
    def __init__(self):
        self.nodes = []

    def createNode(self, name, processType):
        node = ProcessingNode(name, processType)
        self.nodes.append(node)
        return node

    def getSinks(self):
        return [n for n in self.nodes if not n.outputPorts or not any([op.connectedTo for op in n.outputPorts.values()])]

    def process(self, startNodes=None):
        if not startNodes:
            startNodes = self.getSinks()
        sequence = self.topologicalSort(startNodes)

        logger.info('Start processing (%d / %d node(s), %d sink(s))', len(sequence), len(self.nodes), len(startNodes))
        for n in reversed(sequence):
            n.process()
        logger.info('Finished processing')

    def topologicalSort(self, startNodesRef):
        startNodes = list(startNodesRef)
        # TODO: check for cycles by testing for leftover edges when done
        # copy the main graph structure
        pureGraph =  {n : n.getConnectedNodes() for n in self.nodes}

        sequence = []
        while startNodes:
            n = startNodes.pop()
            sequence.append(n)
            for pn in pureGraph[n][0]:
                pureGraph[pn][1].remove(n)
                if len(pureGraph[pn][1]) == 0:
                    startNodes.append(pn)
            pureGraph[n][0] = []

        return sequence


##
# @brief A node bundles a process with input and output ports.
class ProcessingNode:
    @classmethod
    def connectPorts(self, portFrom, portTo):
        if portFrom.direction == portTo.direction:
            logger.error('Cannot connect [%s:%s] to [%s:%s], both are of the same type ("%s").', \
                portFrom.node.name, portFrom.name, portTo.node.name, portTo.name, portTo.direction)
            return False
        elif len(portTo.connectedTo) >= 1:
            logger.error('Cannot connect [%s:%s] to [%s:%s], sink is already connected.',
                portFrom.node.name, portFrom.name, portTo.node.name, portTo.name)
            return false

        portFrom.connectedTo.add(portTo)
        portTo.connectedTo.add(portFrom)
        if not portFrom.fileObj:
            portFrom.fileObj = tempfile.NamedTemporaryFile(delete = False)
        portTo.fileObj = open(portFrom.fileObj.name, 'rb')

        logger.debug('Connected [%s:%s] =>(%s)=> [%s:%s]', portFrom.node.name,\
                portFrom.name, portFrom.fileObj.name, portTo.node.name, portTo.name)
        return True

    @classmethod
    def disconnectPorts(self, portFrom, portTo):
        try:
            portFrom.connectedTo.remove(portTo)
            portTo.connectedTo.remove(portFrom)
            portFrom.fileObj.close()
            portTo.fileObj.close()
            os.unlink(portFrom.name)
        except Exception as e:
            logger.error('Failed to disconnect [%s:%s] =x= [%s:%s]: %s', portFrom.node.name, portFrom.name, portTo.node.name, portTo.name, e.message)

        logger.debug('Disconnected [%s:%s] =x= [%s:%s]', portFrom.node.name, portFrom.name, portTo.node.name, portTo.name)
        return False

    def __init__(self, name, processType):
        self.name = name
        if processType == "":
            self.proc = Process(name)
        elif processType == "const":
            self.proc = ConstantProcess(name)
        elif processType == "add":
            self.proc = AdditionProcess(name)
        elif processType == "print":
            self.proc = PrinterProcess(name)
        elif processType == "bash":
            self.proc = BashProcess(name)
        elif processType == "matlab":
            self.proc = MatlabProcess(name)

        # create ports
        portSpecs = self.proc.getPortSpecs()
        self.inputPorts = {ip : Port(self, ip, 'in') for ip in portSpecs[0]}
        self.outputPorts = {op : Port(self, op, 'out') for op in portSpecs[1]}

    def getParams(self):
        return self.proc.getParams()

    ##
    # @brief Sets parameter <name> to value <value>
    # This method does not create new parameters.
    def setParam(self, name, value):
        if name in self.parameters:
            self.parameters[name] = value
            return True
        else:
            return False

    def getConnectedNodes(self):
        predecNodes = set([port.node for inPort in self.inputPorts.values() if inPort.connectedTo for port in inPort.connectedTo])
        succesNodes = set([port.node for outPort in self.outputPorts.values() if outPort.connectedTo for port in outPort.connectedTo])
        return [predecNodes, succesNodes]

    def process(self):
        inFiles = [inPort.fileObj.name if inPort.fileObj else None for inPort in self.inputPorts.values()]
        outFiles = [outPort.fileObj.name if outPort.fileObj else None for outPort in self.outputPorts.values()]
        if all(inFiles) and all(outFiles):
            logger.debug('Executing process')
            self.proc.run(inFiles, outFiles)
        else:
            logger.warning('One or more ports are not connected. Node "%s" will not be processed!', self.name)


##
# @brief A port represents one of possibly many inputs or outputs of a node.
# If an output port is created, a filesystem pipe is created along with it
class Port:
    def __init__(self, node, name, direction):
        self.node = node
        self.name = name
        self.direction = direction
        self.connectedTo = set()

        self.fileObj = None


    def __del__(self):
        pass
        #if self.fileObj:
        #    os.unlink(self.fileObj)
