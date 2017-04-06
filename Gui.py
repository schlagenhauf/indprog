#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GFlow', '0.2')
gi.require_version('GtkFlow', '0.2')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GFlow
from gi.repository import GtkFlow

import sys

class ExampleNode(GFlow.SimpleNode):
    def __new__(cls, *args, **kwargs):
        x = GFlow.SimpleNode.new()
        x.__class__ = cls
        return x

class StringNode(ExampleNode):
    def __init__(self):
        ExampleNode.__init__(self)

        self.source = GFlow.SimpleSource.new("")
        self.source.set_name("output")
        self.source.set_valid()
        self.add_source(self.source)

        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.do_changed)

        self.set_name("String")

    def do_changed(self, widget=None, data=None):
        self.source.set_value(self.entry.get_text())

class PrintNode(ExampleNode):
    def __init__(self):
        self.sink = GFlow.SimpleSink.new("")
        self.sink.set_name("")
        self.sink.connect("changed", self.do_printing)
        self.add_sink(self.sink)

        self.childlabel = Gtk.Label()

        self.set_name("Output")

    def do_printing(self, dock, val=None):
        try:
            v = self.sink.get_value()
            self.childlabel.set_text(v)
        except:
            self.childlabel.set_text("")

class MeadpipeGui(object):
    def __init__(self):
        w = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.nv = GtkFlow.NodeView.new()
        self.nv.set_show_types(True)

        """
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        create_printnode_button = Gtk.Button("Create PrintNode")
        create_printnode_button.connect("clicked", self.do_create_printnode)
        hbox.add(create_printnode_button)
        create_stringnode_button = Gtk.Button("Create StringNode")
        create_stringnode_button.connect("clicked", self.do_create_stringnode)
        hbox.add(create_stringnode_button)

        vbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(self.nv, True, True, 0)

        w.add(vbox)
        """
        w.add(self.nv)
        w.show_all()
        w.connect("destroy", self.do_quit)
        Gtk.main()

    def do_create_printnode(self, widget=None, data=None):
        n = PrintNode()
        self.nv.add_with_child(n, n.childlabel)
        self.nv.set_show_types(True)

    def do_create_stringnode(self, widget=None, data=None):
        n = StringNode()
        self.nv.add_with_child(n, n.entry)

    def do_quit(self, widget=None, data=None):
        Gtk.main_quit()
        sys.exit(0)

if __name__ == "__main__":
    MeadpipeGui()
