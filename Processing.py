#!/usr/bin/env python3


class ProcessingGraph:
    def __init__(self):
        self.nodes = []


    def addNode(self, node):
        self.nodes.append(node)


    def connectPorts(self, portA, portB):
        if portA.direction == portB.direction:
            return False
        else:
            portA.connectedTo = portB
            portB.connectedTo = portA
            return True


    def process(self, node):
        nodeList = self.getNodesRecurs(node)
        print(nodeList)
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



class ProcessingNode:
    def __init__(self, name):
        self.name = name
        self.inputPorts = [Port(self, "in")]
        self.outputPorts = [Port(self, "out")]
        self.proc = Process()

    def process(self):
        print('Node ' + self.name + ':')
        self.proc.setInData([ip.data for ip in self.inputPorts])
        self.proc.run()
        outdata = self.proc.getOutData()


class Port:
    def __init__(self, node, direction):
        self.node = node
        self.direction = direction
        self.connectedTo = None
        self.data = ""


class Process:
    def __init__(self):
        pass

    def setInData(self, indata):
        pass

    def getOutData(self):
        pass

    def run(self):
        print('\tprocessing...')


if __name__ == '__main__':
    graph = ProcessingGraph()
    node1 = ProcessingNode("node1")
    node2 = ProcessingNode("node2")
    node2.inputPorts.append(Port(node2, "in"));
    node3 = ProcessingNode("node3")
    node4 = ProcessingNode("node4")
    graph.addNode(node1)
    graph.addNode(node2)
    graph.addNode(node3)
    graph.addNode(node4)
    graph.connectPorts(node1.outputPorts[0], node2.inputPorts[0])
    graph.connectPorts(node3.outputPorts[0], node1.inputPorts[0])
    graph.connectPorts(node4.outputPorts[0], node2.inputPorts[1])
    graph.process(node2)
