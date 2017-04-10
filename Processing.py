#!/usr/bin/env python3

import os
import struct
from abc import ABC, abstractmethod


class ProcessingGraph:
    def __init__(self):
        self.nodes = []

    def createNode(self, name, processType):
        node = ProcessingNode(name, processType)
        self.nodes.append(node)
        return node

    def process(self, node=None):
        if not node:
            node = self.nodes[-1]
        nodeList = self.getNodesRecurs(node)
        for n in nodeList:
            n.process()

    def getNodesRecurs(self, node):
        # get connected nodes via the ports (list comprehension orgy)
        predecNodes = set([port.node for inPort in node.inputPorts.values() if inPort.connectedTo for port in inPort.connectedTo])

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
    @classmethod
    def connectPorts(self, portFrom, portTo):
        if portFrom.direction == portTo.direction or portFrom.connectedTo or portTo.connectedTo:
            return False
        else:
            # if there is already someone connected to this sink / input
            if len(portTo.connectedTo) >= 1:
                return false
            portFrom.connectedTo.add(portTo)
            portTo.connectedTo.add(portFrom)
            portTo.data = portFrom.data
            return True

    @classmethod
    def disconnectPorts(self, portFrom, portTo):
        print("DISCONNECTING PORTS NOT IMPLEMENTED!!!")
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


    def process(self):
        inFds = [ip.data[0] for ip in self.inputPorts.values()]
        outFds = [op.data[1] for op in self.outputPorts.values()]
        self.proc.run(inFds, outFds)


##
# @brief A port represents one of possibly many inputs or outputs of a node.
# If an output port is created, a filesystem pipe is created along with it
class Port:
    def __init__(self, node, name, direction):
        self.node = node
        self.name = name
        self.direction = direction
        self.connectedTo = set()

        if direction == "in":
            self.data = None
        else:
            self.data = os.pipe()


##
# @brief Wrapper for the process that a node represents. Can wrap a variety of actions.
class Process(ABC):
    def __init__(self, name):
        self.name = name
        self.params = {}

    ##
    # @brief Returns the port specifications of this process so that the containing node
    # can create them
    #
    # @return List of port specifications
    @abstractmethod
    def getPortSpecs(self):
        pass


    ##
    # @brief Returns a reference to the parameter dictionary
    #
    # @return Dictionary of parameter names and values
    def getParams(self):
        return self.params

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
                    print(self.name)
                    print(struct.unpack('f', line)[0])
                    print('\t' + '0x' + ' 0x'.join(format(b, '02x') for b in line))


class ConstantProcess(Process):
    def __init__(self, name):
        super(ConstantProcess, self).__init__(name)
        self.constant = 9.0
        self.params = {'value': 1, 'another value' : 123}

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
        print('Adding: ')
        for i in inFds:
            iop = os.fdopen(i, 'rb')
            if iop:
                data = iop.read()
                val = struct.unpack('f', data)[0]
                print(' + ' + str(val))
                valSum += val
                iop.close()

        print(' = ' + str(valSum))

        oop = os.fdopen(outFds[0], 'wb')
        if oop:
            data = struct.pack('f',valSum)
            oop.write(data)
            oop.close()
