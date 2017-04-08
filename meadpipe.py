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

        self.createHud()

        self.fgui = FlowGui(self.w, self.vbox)
        self.procGraph = ProcessingGraph()

    def __quit(self, widget=None, data=None):
        Gtk.main_quit()
        sys.exit(0)

    def __createNode(self, nodeType, widget=None, data=None):
        node = ProcessingNode('node1', nodeType)
        ins, outs = node.proc.getPortSpecs()
        params = node.proc.getParams()
        self.fgui.createFlowNode(ins, outs, params)
        self.procGraph.addNode(node)


    def createHud(self):
        btnBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        btn = Gtk.Button("Create Const Node")
        btn.connect("clicked", lambda w = None, d = None: self.__createNode('const', w, d))
        btnBox.add(btn)

        btn = Gtk.Button("Create Add Node")
        btn.connect("clicked", lambda w = None, d = None: self.__createNode('add', w, d))
        btnBox.add(btn)

        btn = Gtk.Button("Create Print Node")
        btn.connect("clicked", lambda w = None, d = None: self.__createNode('print', w, d))
        btnBox.add(btn)

        self.vbox.pack_start(btnBox, False, False, 0)

        self.w.add(self.vbox)

    def run(self):
        self.w.show_all()
        Gtk.main()

if __name__ == '__main__':
    mp = Meadpipe()
    mp.run()
