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

from Processing import ProcessingGraph
from Gui import FlowGui

class Meadpipe(object):
    def __init__(self):
        self.w = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.w.connect("destroy", self.__quit)

        self.gui = FlowGui()
        self.gui.populate(self.w)

        self.procGraph = ProcessingGraph()


    def __quit(self, widget=None, data=None):
        Gtk.main_quit()
        sys.exit(0)

    def run(self):
        self.w.show_all()
        Gtk.main()

if __name__ == '__main__':
    mp = Meadpipe()
    mp.run()
