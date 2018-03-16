#!/usr/bin/env python3

from Processing import *


pg = ProcessingGraph()

# create nodes
c1 = pg.createNode('const1', 'const');
c2 = pg.createNode('const2', 'const');
a = pg.createNode('add', 'add');
p = pg.createNode('print', 'print');

# connect ports
ProcessingNode.connectPorts(c1.outputPorts['out'], a.inputPorts['summand1'])
ProcessingNode.connectPorts(c2.outputPorts['out'], a.inputPorts['summand2'])
ProcessingNode.connectPorts(a.outputPorts['sum'], p.inputPorts['in'])

# save to file and load again
pg.saveToFile('testfile.xml')
pg.loadFromFile('testfile.xml')

# check if everything is still there
