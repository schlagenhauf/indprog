import os
import struct
from abc import ABC, abstractmethod
import uuid
import tempfile
import logging
import xml.etree.cElementTree as ET
from xml.dom import minidom

from Wrappers import *

logger = logging.getLogger(__name__)


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
        wentWell = True
        for n in reversed(sequence):
            if not n.process():
                wentWell = False
                break

        if wentWell:
            logger.info('Finished processing')
        else:
            logger.critical('Processing failed. Aborting.')


    def topologicalSort(self, startNodesRef):
        startNodes = list(startNodesRef)
        # TODO: check for cycles by testing for leftover edges when done
        # copy the main graph structure
        pureGraph =  {n : n.getConnectedNodes() for n in self.nodes}

        sequence = []
        while startNodes:
            n = startNodes.pop()
            if not n.isUpToDate():
                sequence.append(n)
            for pn in pureGraph[n][0]:
                pureGraph[pn][1].remove(n)
                if len(pureGraph[pn][1]) == 0:
                    startNodes.append(pn)
            pureGraph[n][0] = []

        return sequence


    def generateUniquePortIds(self):
        portIdCounter = 0
        for n in self.nodes:
            for ik in n.inputPorts.keys():
                n.inputPorts[ik].id = portIdCounter
                portIdCounter += 1

            for ok in n.outputPorts.keys():
                n.outputPorts[ok].id = portIdCounter
                portIdCounter += 1


    def saveToFile(self, path):
        self.generateUniquePortIds()

        # save as XML. required values are attributes, optional values are content
        root = ET.Element('graph')

        for n in self.nodes:
            xmlnode = ET.SubElement(root, 'node', name=n.name, type=n.procType)

            if n.guiNode:
                pos = n.guiNode.getPosition()
                ET.SubElement(xmlnode, 'gui', pos_x=str(pos.x), pos_y=str(pos.y))

            xmlparams = ET.SubElement(xmlnode, 'parameters')
            for pk, pv in n.getParams().items():
                ET.SubElement(xmlparams, 'parameter', key=pk, value=pv)

            xmlports = ET.SubElement(xmlnode, 'ports')
            for ip in n.inputPorts.values():
                xmlport = ET.SubElement(xmlports, 'inport', name=ip.name, id=str(ip.id))

            for op in n.outputPorts.values():
                xmlport = ET.SubElement(xmlports, 'outport', name=op.name, id=str(op.id))
                for to in op.connectedTo:
                    ET.SubElement(xmlport, 'connectedto', id=str(to.id))


        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="\t")

        with open(path, 'w') as f:
            f.write(xmlstr)


    def loadFromFile(self, path):
        self.nodes = [] # TODO: check if circular refs slow down deletion

        try:
            with open(path, 'r') as f:
                try:
                    xmlstr = f.read()
                    root = ET.fromstring(xmlstr)

                    # map from ID to port object
                    portMap = {}
                    connections = [];

                    # set up nodes
                    for xmlnode in root:
                        procNode = self.createNode(xmlnode.attrib['name'], xmlnode.attrib['type'])

                        # delete ports created by process TODO: don't delete, try to match
                        procNode.outputPorts = {}
                        procNode.inputPorts = {}

                        # get gui node position
                        xmlgui = xmlnode.find('gui')
                        procNode.guiPos = (int(xmlgui.attrib['pos_x']), int(xmlgui.attrib['pos_y']))

                        # get ports
                        for po in xmlnode.find('ports'):
                            if po.tag == 'outport':
                                pname = po.attrib['name']
                                procNode.outputPorts[pname] = Port(procNode, pname, 'out')
                                procNode.outputPorts[pname].id = po.attrib['id']
                                portMap[po.attrib['id']] = procNode.outputPorts[pname]
                                for con in po:
                                    connections.append((po.attrib['id'], con.attrib['id']))

                            elif po.tag == 'inport':
                                pname = po.attrib['name']
                                procNode.inputPorts[pname] = Port(procNode, pname, 'in')
                                procNode.inputPorts[pname].id = po.attrib['id']
                                portMap[po.attrib['id']] = procNode.inputPorts[pname]


                        paramList = xmlnode.find('parameters')
                        if paramList:
                            for pa in paramList:
                                procNode.createParam(pa.attrib['key'], pa.attrib['value'])

                        procNode.initProcess()


                    # connect ports
                    for con in connections:
                        ProcessingNode.connectPorts(portMap[con[0]], portMap[con[1]])
                except ET.ParseError as pe:
                    logger.critical('An error occured while loading the XML file: %s' % str(pe))
                    self.nodes = []
        except IOError as ioe:
            logger.critical('Error while opening file: %s' % str(ioe))


    def __str__(self):
        return "Number of nodes: %d" % len(self.nodes)


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
        if not portFrom.fileObj:
            portFrom.fileObj = tempfile.NamedTemporaryFile(delete = False)
        portTo.fileObj = open(portFrom.fileObj.name, 'rb')

        logger.debug('Connected [%s:%s] =>(%s)=> [%s:%s]', portFrom.node.name,\
                portFrom.name, portFrom.fileObj.name, portTo.node.name, portTo.name)
        return True

    @classmethod
    def disconnectPorts(self, portFrom, portTo):
        names = (portFrom.node.name, portFrom.name, portTo.node.name, portTo.name)
        try:
            logger.debug('PortFrom: ' + str(portFrom))
            logger.debug('PortTo: ' + str(portTo))

            portFrom.connectedTo.remove(portTo)
            portTo.connectedTo.remove(portFrom)
            portTo.fileObj.close()
            portTo.fileObj = None

            # if no sink ports are connected anymore, close the file
            if not portFrom.connectedTo:
                portFrom.fileObj.close()
                os.remove(portFrom.fileObj.name)
                portFrom.fileObj = None

        except Exception as e:
            logger.critical('Failed to disconnect [%s:%s] =x= [%s:%s]', *names)
            logger.exception(e)
            return False

        logger.debug('Disconnected [%s:%s] =x= [%s:%s]', *(names))
        return True

    def __init__(self, name, processType):
        self.name = name
        self.procType = processType
        if processType == "":
            self.proc = Process(name)
        elif processType == "dummy":
            self.proc = DummyProcess(name)
        elif processType == "fileread":
            self.proc = FileReadProcess(name)
        elif processType == "filewrite":
            self.proc = FileWriteProcess(name)
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
        else:
            logger.error('Process type "%s" not supported!' % processType)

        # create ports
        portSpecs = self.proc.getPortSpecs()
        self.inputPorts = {ip : Port(self, ip, 'in') for ip in portSpecs[0]}
        self.outputPorts = {op : Port(self, op, 'out') for op in portSpecs[1]}

        # only used when a gui is drawing the nodes
        self.guiNode = None
        self.guiPos = (0,0)

    def initProcess(self):
        self.proc.init()

    def getParam(self, key):
        return self.proc.params[key]

    def getParams(self):
        return self.proc.getParams()

    def isUpToDate(self):
        return all([p.isUpToDate() for p in self.inputPorts.values()]) \
                and self.proc.isUpToDate()

    def isReady(self):
        pass

    def createParam(self, key, value):
        self.proc.params[key] = value;

    ##
    # @brief Sets parameter <name> to value <value>
    # This method does not create new parameters.
    def setParam(self, name, value):
        if name in self.proc.params:
            self.proc.params[name] = value
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
            logger.debug('Executing process "%s"', self.name)
            try:
                self.proc.run(inFiles, outFiles)
                return True
            except Exception as e:
                logger.error('Error while executing process %s: %s' % (self.name, str(e)))
                return False
        else:
            notConnectedPorts = [inPort.name for inPort in self.inputPorts.values() if not inPort.fileObj]\
                + [outPort.fileObj for outPort in self.outputPorts.values() if not outPort.fileObj]

            logger.error('The following ports of node "%s" are not connected: ' % self.name)
            for nc in notConnectedPorts:
                logger.error('\tPort "%s"' % nc)
            return False

    def __str__(self):
        return 'Processing Node "%s", %d input ports, %d output ports' % (self.name, len(self.inputPorts), len(self.outputPorts))


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

        self.id = -1 # for saving / loading


    def __del__(self):
        pass
        #if self.fileObj:
        #    os.unlink(self.fileObj)

    def isUpToDate(self):
        return False

    def __str__(self):
        foName = self.fileObj.name if self.fileObj else str(None)
        return 'Port "%s", parent node: "%s", direction: %s, tempfile name: %s, %d connections: %s' \
                % (self.name, self.node.name, self.direction, foName, len(self.connectedTo), \
                str([p.name for p in self.connectedTo]))
