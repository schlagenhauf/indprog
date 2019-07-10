#!/usr/bin/env python3

import sys
import argparse

import logging
logger = logging.getLogger(__name__)

from Processing import ProcessingGraph, ProcessingNode
from Wrappers import DummyProcess

class Indprog:
    def __init__(self):
        self.procGraph = ProcessingGraph()

        # test node
        proc = DummyProcess("dummyProc");
        n1 = self.__createNode(proc)
        n2 = self.__createNode(proc)
        n3 = self.__createNode(proc)

        # test connecting
        ProcessingNode.connectPorts(n1.outputPorts['outport'], n2.inputPorts['inport'])

        # test disconnecting
        ProcessingNode.connectPorts(n2.outputPorts['outport'], n3.inputPorts['inport'])
        ProcessingNode.disconnectPorts(n2.outputPorts['outport'], n3.inputPorts['inport'])


    def __quit(self):
        sys.exit(0)

    def __createNode(self, process):
        node = self.procGraph.createNode('node_' + process.name, process)
        return node

    def __executeGraph(self):
        self.procGraph.process()

    def run(self):
        self.__executeGraph();

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], \
            help="Set the logging level")

    args = parser.parse_args()
    if args.logLevel:
        lvl = logging.getLevelName(args.logLevel)
    else:
        lvl = logging.WARNING

    logging.basicConfig(
            level=lvl,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%H:%M:%S", stream=sys.stdout)

    logger.info('Starting...')
    mp = Indprog()
    mp.run()
    logger.info('Quitting')
