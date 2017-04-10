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

    def __init__(self, procNode):
        self.procNode = procNode
        self.setPorts([p.name for p in procNode.inputPorts], [p.name for p in procNode.outputPorts])
        self.setParams(procNode.getParams())
        self.set_name(procNode.name)

        self.paramBox = Gtk.ListBox()
        for k,v in self.procNode.getParams().items():
            hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, 0)
            label = Gtk.Label(k)
            hbox.pack_start(label, True, True, 0)
            entry = Gtk.Entry()
            hbox.pack_start(entry, True, True, 0)
            row = Gtk.ListBoxRow()
            row.add(hbox)
            self.paramBox.add(row)


    def setPorts(self, ins, outs):
        for i in ins:
            sink = GFlow.SimpleSink.new("")
            sink.set_name(i)
            self.add_sink(sink)

        for o in outs:
            source = GFlow.SimpleSource.new("")
            source.set_name(o)
            source.set_valid()
            self.add_source(source)

    def setParams(self, paramDict):
        pass


    def do_changed(self, widget=None, data=None):
        self.source.set_value(self.entry.get_text())

class FlowGui(object):
    def __init__(self, w, vbox):
        self.nv = GtkFlow.NodeView.new()
        self.nv.set_show_types(True)
        vbox.pack_end(self.nv, True, True, 0)
        w.add(self.nv)

    def createFlowNode(self, procNode):
        n = FlowGuiNode(procNode)
        self.nv.add_with_child(n, n.paramBox)
        #self.nv.add_node(n)
