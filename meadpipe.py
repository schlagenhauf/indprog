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
import argparse

import logging

logger = logging.getLogger(__name__)

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

    def __loadGraph(self, widget=None, data=None):
        dialog = Gtk.FileChooserDialog('Load Graph From File', self.w,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL \
            or response == Gtk.ResponseType.CLOSE \
            or response == Gtk.ResponseType.DELETE_EVENT:
            print("Cancel clicked")

        dialog.destroy()

    def __saveGraph(self, widget=None, data=None):
        print('blasave')

    def __executeGraph(self, widget=None, data=None):
        self.procGraph.process()

    def createHud(self):
        self.tools = Gtk.ToolPalette()

        # general functions
        generalTools = Gtk.ToolItemGroup.new('General')
        self.tools.add(generalTools)

        loadItem = Gtk.ToolButton.new(None, 'Load')
        loadItem.connect("clicked", self.__loadGraph)
        generalTools.insert(loadItem, -1)

        saveItem = Gtk.ToolButton.new(None, 'Save')
        saveItem.connect("clicked", self.__saveGraph)
        generalTools.insert(saveItem, -1)

        runItem = Gtk.ToolButton.new(None, 'Run')
        runItem.connect("clicked", self.__executeGraph)
        generalTools.insert(runItem, -1)

        # node functions
        newNodeTools = Gtk.ToolItemGroup.new('New Node')
        self.tools.add(newNodeTools)

        constNodeItem = Gtk.ToolButton.new(None, 'FileRead')
        constNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('fileread', w, d))
        newNodeTools.insert(constNodeItem, -1)

        constNodeItem = Gtk.ToolButton.new(None, 'FileWrite')
        constNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('filewrite', w, d))
        newNodeTools.insert(constNodeItem, -1)

        constNodeItem = Gtk.ToolButton.new(None, 'Constant')
        constNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('const', w, d))
        newNodeTools.insert(constNodeItem, -1)

        printNodeItem = Gtk.ToolButton.new(None, 'Printer')
        printNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('print', w, d))
        newNodeTools.insert(printNodeItem, -1)

        adderNodeItem = Gtk.ToolButton.new(None, 'Adder')
        adderNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('add', w, d))
        newNodeTools.insert(adderNodeItem, -1)

        adderNodeItem = Gtk.ToolButton.new(None, 'Bash')
        adderNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('bash', w, d))
        newNodeTools.insert(adderNodeItem, -1)

        adderNodeItem = Gtk.ToolButton.new(None, 'MatLab')
        adderNodeItem.connect("clicked", lambda w = None, d = None: self.__createNode('matlab', w, d))
        newNodeTools.insert(adderNodeItem, -1)

        self.vbox.pack_start(self.tools, False, False, 0)

        vsep = Gtk.VSeparator()
        self.vbox.pack_start(vsep, False, False, 0)

        logger.debug('HUD populated')


    def run(self):
        self.w.show_all()
        Gtk.main()

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
    mp = Meadpipe()
    mp.run()
    logger.info('Quitting')
