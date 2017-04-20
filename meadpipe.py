#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GFlow', '0.2')
gi.require_version('GtkFlow', '0.2')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GFlow
from gi.repository import GtkFlow

import sys

from Processing import ProcessingGraph, ProcessingNode
from Gui import FlowGui

class Meadpipe(object):
    def __init__(self):
        self.w = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.w.connect("destroy", self.__quit)
        self.vbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.w.add(self.vbox)

        self.createHud()

        self.fgui = FlowGui(self.w, self.vbox)
        self.procGraph = ProcessingGraph()

    def __quit(self, widget=None, data=None):
        Gtk.main_quit()
        sys.exit(0)

    def __createNode(self, nodeType, widget=None, data=None):
        node = self.procGraph.createNode('node_' + nodeType, nodeType)
        self.fgui.createFlowNode(node)

    def __executeGraph(self, widget=None, data=None):
        self.procGraph.process()

    def createHud(self):
        self.tools = Gtk.ToolPalette()

        # general functions
        generalTools = Gtk.ToolItemGroup.new('General')
        self.tools.add(generalTools)

        runItem = Gtk.ToolButton.new(None, 'Run')
        runItem.connect("clicked", self.__executeGraph)
        generalTools.insert(runItem, -1)

        # node functions
        newNodeTools = Gtk.ToolItemGroup.new('New Node')
        self.tools.add(newNodeTools)

        constNodeItem = Gtk.ToolButton.new(None, 'Constant')
        constNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('const', w, d))
        newNodeTools.insert(constNodeItem, -1)

        printNodeItem = Gtk.ToolButton.new(None, 'Printer')
        printNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('print', w, d))
        newNodeTools.insert(printNodeItem, -1)

        adderNodeItem = Gtk.ToolButton.new(None, 'Adder')
        adderNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('add', w, d))
        newNodeTools.insert(adderNodeItem, -1)

        self.vbox.pack_start(self.tools, False, False, 0)

        vsep = Gtk.VSeparator()
        self.vbox.pack_start(vsep, False, False, 0)


    def run(self):
        self.w.show_all()
        Gtk.main()

if __name__ == '__main__':
    mp = Meadpipe()
    mp.run()
