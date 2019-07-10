import os
import struct
from abc import ABC, abstractmethod
import uuid
import tempfile
import logging

from Wrappers import *

logger = logging.getLogger(__name__)

class ProcessingGraph:
    def __init__(self):
        self.nodes = []


    def createNode(self, name, process):
        node = ProcessingNode(name, process)
        self.nodes.append(node)
        return node


    # Get all sinks among the nodes. A sink is classified as a node without (connected) output ports.
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
            if not n.upToDate():
                sequence.append(n)
            for pn in pureGraph[n][0]:
                pureGraph[pn][1].remove(n)
                if len(pureGraph[pn][1]) == 0:
                    startNodes.append(pn)
            pureGraph[n][0] = []

        return sequence

    def saveToFile(self, path):
        pass

    def loadFromFile(self, path):
        pass


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
            return False

        portFrom.connectedTo.add(portTo)
        portTo.connectedTo.add(portFrom)

        logger.debug('Connected [%s:%s] => [%s:%s]', portFrom.ownerNode.name,\
                portFrom.name, portTo.ownerNode.name, portTo.name)
        return True

    @classmethod
    def disconnectPorts(self, portFrom, portTo):
        logger.debug('PortFrom: ' + str(portFrom))
        logger.debug('PortTo: ' + str(portTo))

        portFrom.connectedTo.remove(portTo)
        portTo.connectedTo.remove(portFrom)

        names = (portFrom.ownerNode.name, portFrom.name, portTo.ownerNode.name, portTo.name)
        logger.debug('Disconnected [%s:%s] =x= [%s:%s]', *(names))
        return True

    def __init__(self, name, process):
        self.name = name
        self.proc = process

        # create ports
        self.inputPorts = {ip : Port(self, ip, 'in') for ip in self.proc.portSpecs[0]}
        self.outputPorts = {op : Port(self, op, 'out') for op in self.proc.portSpecs[1]}

    def upToDate(self):
        return all([p.upToDate() for p in self.inputPorts.values()]) \
                and self.proc.upToDate()

    def getConnectedNodes(self):
        predecNodes = set([port.ownerNode for inPort in self.inputPorts.values() if inPort.connectedTo for port in inPort.connectedTo])
        succesNodes = set([port.ownerNode for outPort in self.outputPorts.values() if outPort.connectedTo for port in outPort.connectedTo])
        return [predecNodes, succesNodes]

    def process(self):
        # TODO find a replacement for files
        #inFiles = [inPort.fileObj.name if inPort.fileObj else None for inPort in self.inputPorts.values()]
        #outFiles = [outPort.fileObj.name if outPort.fileObj else None for outPort in self.outputPorts.values()]
        inData = {}
        outData = {}

        # TODO find way to check if IO is ok
        if True:
            logger.debug('Executing process "%s"', self.name)
            self.proc.run(inData, outData)
        else:
            logger.warning('One or more ports are not connected. Node "%s" will not be processed!', self.name)

    def __str__(self):
        return 'Processing Node "%s", %d input ports, %d output ports' % (self.name, len(self.inputPorts), len(self.outputPorts))


##
# @brief A port represents one of possibly many inputs or outputs of a node.
class Port:
    def __init__(self, node, name, direction):
        self.ownerNode = node
        self.name = name
        self.direction = direction
        self.connectedTo = set()

    def __del__(self):
        pass

    def upToDate(self):
        return False

    def __str__(self):
        return 'Port "%s", owner node: "%s", direction: %s, %d connections: %s' \
                % (self.name, self.ownerNode.name, self.direction, len(self.connectedTo), \
                str([p.name for p in self.connectedTo]))
