#!/usr/bin/env python3

import os


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
    def __init__(self, name, inPorts = [], outPorts = []):
        self.name = name
        self.inputPorts = [Port(self, ip) for ip in inPorts]
        self.outputPorts = [Port(self, op) for op in outPorts]
        self.proc = Process(name)

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

    def run(self, inFds, outFds):
        str = ""
        for i in inFds:
            iop = open(i, 'r')
            if iop:
                str += iop.readline()
                iop.close()

        str += self.name

        print(str)

        for o in outFds:
            oop = open(o, 'w')
            if oop:
                oop.write(str)
                oop.close()

        #print(inFds)
        #print(outFds)
        #print('\tDummy Process...')


class ArithmeticProcess(Process):
    def __init__(self, procType):
        self.procType = procType

    def run(self, inFds, outFds):
        if self.procType == "add":
           outdata.append([inFd[0] + inFd[1]])



if __name__ == '__main__':
    graph = ProcessingGraph()
    node1 = ProcessingNode("node1", ["in"], ["out"])
    node2 = ProcessingNode("node2", ["in1", "in2"], [])
    node3 = ProcessingNode("node3", [], ["out"])
    node4 = ProcessingNode("node4", [], ["out"])
    graph.addNode(node1)
    graph.addNode(node2)
    graph.addNode(node3)
    graph.addNode(node4)
    graph.connectPorts(node1.outputPorts[0], node2.inputPorts[0])
    graph.connectPorts(node3.outputPorts[0], node1.inputPorts[0])
    graph.connectPorts(node4.outputPorts[0], node2.inputPorts[1])
    graph.process(node2)
