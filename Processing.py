#!/usr/bin/env python3

import os
import struct


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
    def __init__(self, name, processType, inPorts = [], outPorts = []):
        self.name = name
        self.inputPorts = [Port(self, ip) for ip in inPorts]
        self.outputPorts = [Port(self, op) for op in outPorts]
        if processType == "":
            self.proc = Process(name)
        elif processType == "const":
            self.proc = ConstantProcess(name)
        elif processType == "add":
            self.proc = AdditionProcess(name)


    def process(self):
        print('Node ' + self.name + ':')
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
class Process:
    def __init__(self, name):
        self.name = name

    ##
    # @brief Returns the port specifications of this process so that the containing node
    # can create them
    #
    # @return List of port specifications
    def getPortSpecs(self):
        pass

    def run(self, inFds, outFds):
        str = ""
        for i in inFds:
            iop = open(i, 'r')
            if iop:
                str += iop.readline()
                iop.close()

        str += self.name

        print('\t' + str)

        for o in outFds:
            oop = open(o, 'w')
            if oop:
                oop.write(str)
                oop.close()


class ConstantProcess(Process):
    def __init__(self, name):
        super(ConstantProcess, self).__init__(name)
        self.constant = 4

    def run(self, inFds, outFds):
        for o in outFds:
            oop = open(o, 'w')
            if oop:
                oop.write(struct.pack('f',self.constant).decode('ascii') + '\n')
                oop.close()


class AdditionProcess(Process):
    def __init__(self, name):
        super(AdditionProcess, self).__init__(name)

    def run(self, inFds, outFds):
        valSum = 0
        for i in inFds:
            iop = open(i, 'r')
            if iop:
                valSum += struct.unpack('f', iop.readline())
                iop.close()

        for o in outFds:
            oop = open(o, 'w')
            if oop:
                oop.write(struct.pack('f',valSum).decode('ascii') + '\n')
                oop.close()



if __name__ == '__main__':
    graph = ProcessingGraph()
    node1 = ProcessingNode("node1", "", ["in"], ["out"])
    node2 = ProcessingNode("node2", "add", ["in1", "in2"], [])
    node3 = ProcessingNode("node3", "const", [], ["out"])
    node4 = ProcessingNode("node4", "const", [], ["out"])
    graph.addNode(node1)
    graph.addNode(node2)
    graph.addNode(node3)
    graph.addNode(node4)
    graph.connectPorts(node1.outputPorts[0], node2.inputPorts[0])
    graph.connectPorts(node3.outputPorts[0], node1.inputPorts[0])
    graph.connectPorts(node4.outputPorts[0], node2.inputPorts[1])
    graph.process(node2)
