#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GFlow', '0.2')
gi.require_version('GtkFlow', '0.2')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GFlow
from gi.repository import GtkFlow


class FlowGuiNode(GFlow.SimpleNode):
    def __new__(cls, *args, **kwargs):
        x = GFlow.SimpleNode.new()
        x.__class__ = cls
        return x

    def __init__(self):

        """
        self.source = GFlow.SimpleSource.new("")
        self.source.set_name("output")
        self.source.set_valid()
        self.add_source(self.source)

        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.do_changed)
        """

        self.set_name("String")

    def setPorts(self, ins, outs):
        for i in ins:
            source = GFlow.SimpleSource.new("")
            source.set_name(i)
            source.set_valid()
            self.add_source(source)

        for o in outs:
            sink = GFlow.SimpleSink.new("")
            sink.set_name(o)
            self.add_sink(sink)


    def setParams(self):
        pass


    def do_changed(self, widget=None, data=None):
        self.source.set_value(self.entry.get_text())

class FlowGui(object):
    def populate(self, gtkWindow):
        self.nv = GtkFlow.NodeView.new()
        self.nv.set_show_types(True)

        btnBox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        btnAddNode = Gtk.Button("Create Node")
        btnAddNode.connect("clicked", self.createFlowNode)
        btnBox.add(btnAddNode)

        vbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        vbox.pack_start(btnBox, False, False, 0)
        vbox.pack_start(self.nv, True, True, 0)

        gtkWindow.add(vbox)
        gtkWindow.add(self.nv)

    def createFlowNode(self, widget=None, data=None):
        n = FlowGuiNode()
        n.setPorts(['in1','in2'],['out1','out2'])
        self.nv.add_node(n)
        return n
