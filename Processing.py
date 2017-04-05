#!/usr/bin/env python3

import os
import struct
from abc import ABC, abstractmethod


class ProcessingGraph:
    def __init__(self):
        self.nodes = []


    def addNode(self, node):
        self.nodes.append(node)


    def connectPorts(self, portFrom, portTo):
        if portFrom.direction == portTo.direction:
            return False
        else:
            portFrom.connectedTo = portTo
            portTo.connectedTo = portFrom
            portTo.data = portFrom.data
            return True


    def process(self, node):
        nodeList = self.getNodesRecurs(node)
        for n in nodeList:
            n.process()

    def getNodesRecurs(self, node):
        # get connected nodes via the ports
        predecNodes = set([inPort.connectedTo.node for inPort in node.inputPorts if inPort.connectedTo])

        # get nodes from predecessors recursively
        nodes = [self.getNodesRecurs(n) for n in predecNodes]

        # flatten list and append this node
        nodes = [m for n in nodes for m in n] + [node]

        return self.uniqueSeq(nodes)

    def uniqueSeq(self, seq):
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]


##
# @brief A node bundles a process with input and output ports.
class ProcessingNode:
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

        portSpecs = self.proc.getPortSpecs()
        self.inputPorts = [Port(self, ip) for ip in portSpecs[0]]
        self.outputPorts = [Port(self, op) for op in portSpecs[1]]


    def process(self):
        inFds = [ip.data[0] for ip in self.inputPorts]
        outFds = [op.data[1] for op in self.outputPorts]
        self.proc.run(inFds, outFds)


##
# @brief A port represents one of possibly many inputs or outputs of a node.
# If an output port is created, a filesystem pipe is created along with it
class Port:
    def __init__(self, node, direction):
        self.node = node
        self.direction = direction
        self.connectedTo = None

        if direction == "in":
            self.data = None
        else:
            self.data = os.pipe()


##
# @brief Wrapper for the process that a node represents. Can wrap a variety of actions.
class Process(ABC):
    def __init__(self, name):
        self.name = name

    ##
    # @brief Returns the port specifications of this process so that the containing node
    # can create them
    #
    # @return List of port specifications
    @abstractmethod
    def getPortSpecs(self):
        pass

    @abstractmethod
    def run(self, inFds, outFds):
        pass
        """
        str = b''
        for i in inFds:
            iop = open(i, 'rb')
            if iop:
                str += iop.readline()
                iop.close()

        #str += self.name

        #print('\t' + str)

        for o in outFds:
            oop = open(o, 'wb')
            if oop:
                oop.write(str)
                oop.close()
        """


class PrinterProcess(Process):
    def __init__(self, name):
        super(PrinterProcess, self).__init__(name)


    def getPortSpecs(self):
        return [['in'],[]]


    def run(self, inFds, outFds):
        for  i in inFds:
            oip = open(i, 'rb')
            if oip:
                while True:
                    line = oip.read()
                    if not line:
                        break
                    print(self.name + ': ' + ''.join(format(b, '02x') for b in line))


class ConstantProcess(Process):
    def __init__(self, name):
        super(ConstantProcess, self).__init__(name)
        self.constant = 4.0

    def getPortSpecs(self):
        return [[],['out']]

    def run(self, inFds, outFds):
        for o in outFds:
            oop = os.fdopen(o, 'wb')
            if oop:
                data = struct.pack('f',self.constant)
                oop.write(data)
                oop.close()


class AdditionProcess(Process):
    def __init__(self, name):
        super(AdditionProcess, self).__init__(name)

    def getPortSpecs(self):
        return [['summand1', 'summand2'],['sum']]

    def run(self, inFds, outFds):
        valSum = 0
        for i in inFds:
            iop = os.fdopen(i, 'rb')
            if iop:
                data = iop.read()
                valSum += struct.unpack('f', data)[0]
                iop.close()

        for o in outFds:
            oop = os.fdopen(o, 'wb')
            if oop:
                data = struct.pack('f',valSum)
                oop.write(data)
                oop.close()



if __name__ == '__main__':
    graph = ProcessingGraph()
    node2 = ProcessingNode("node2", "add")
    node3 = ProcessingNode("node3", "const")
    node4 = ProcessingNode("node4", "const")
    node5 = ProcessingNode("node5", "print")
    graph.addNode(node2)
    graph.addNode(node3)
    graph.addNode(node4)
    graph.addNode(node5)
    graph.connectPorts(node3.outputPorts[0], node2.inputPorts[0])
    graph.connectPorts(node4.outputPorts[0], node2.inputPorts[1])
    graph.connectPorts(node2.outputPorts[0], node5.inputPorts[0])
    graph.process(node5)
