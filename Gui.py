#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GFlow', '0.2')
gi.require_version('GtkFlow', '0.2')
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import GFlow
from gi.repository import GtkFlow
from gi.repository.Gdk import Color
from gi.repository import Gdk

import logging
logger = logging.getLogger(__name__)

class FlowGuiNode(GFlow.SimpleNode):
    #COLOR_INVALID = Gdk.RGBA(255,0,0)
    COLOR_INVALID = Color(50000, 0, 0)

    def __new__(cls, *args, **kwargs):
        x = GFlow.SimpleNode.new()
        x.__class__ = cls
        return x

    def __init__(self, procNode, nv):
        self.procNode = procNode
        self.procNode.guiNode = self

        self.nv = nv

        self.portMap = {}
        self.setPorts([p for p in procNode.inputPorts.keys()], [p for p in procNode.outputPorts.keys()])

        self.set_name(procNode.name)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        label = Gtk.Label.new(procNode.name)
        self.vbox.pack_start(label, False, False, 0)
        self.generateParamBox()

        self.disableLinkingCb = False

    def __del__(self):
        logger.critical('DTOR not implemented!')

    def generateParamBox(self):
        if len(self.procNode.getParams()) == 0:
            return

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.vbox.pack_start(sep, False, False, 0)

        self.expander = Gtk.Expander.new('Parameters')
        self.expander.set_resize_toplevel(True)

        self.paramBox = Gtk.ListBox()
        for k,v in self.procNode.getParams().items():
            hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, 0)
            label = Gtk.Label(k)
            label.set_xalign(0)
            hbox.pack_start(label, True, True, 0)
            entry = Gtk.Entry()
            entry.set_text(str(v))
            entry.set_alignment(1)
            entry.set_has_frame(False)
            entry.connect('changed', lambda w, d=None, key=k: self.__paramChanged(w, key))
            hbox.pack_start(entry, True, True, 0)
            row = Gtk.ListBoxRow()
            row.add(hbox)
            self.paramBox.add(row)

        self.expander.add(self.paramBox)
        self.vbox.pack_end(self.expander, True, True, 0)

    def setPorts(self, ins, outs):
        for i in ins:
            sink = GFlow.SimpleSink.new("")
            sink.set_name(i)
            self.add_sink(sink)
            self.portMap[i] = sink

        for o in outs:
            source = GFlow.SimpleSource.new("")
            source.set_name(o)
            source.connect("linked", self.__onSourceLink)
            source.connect("unlinked", self.__onSourceUnlink)
            self.add_source(source)
            self.portMap[o] = source

    def getPosition(self):
        return self.nv.get_node_position(self)

    def __paramChanged(self, gtkEntry, key):
        valStr = gtkEntry.get_text()
        try:
            val = type(self.procNode.getParam(key))(valStr)
            if self.procNode.setParam(key, val):
                logger.debug('Changing parameter "%s" to value "%s"', key, val)
            else:
                logger.error('Failed to change parameter "%s" to value "%s"', key, val)
            #gtkEntry.modify_base(Gtk.StateFlags.NORMAL, None)
        except (TypeError, ValueError) as e:
            #gtkEntry.modify_base(Gtk.StateType.GTK_STATE_NORMAL, FlowGuiNode.COLOR_INVALID)
            logger.error('Incompatible type for parameter "%s" (must be %s)', key, str(type(self.procNode.getParam(key))))

    def __onSourceLink(self, sourceDock, sinkDock):
        if self.disableLinkingCb:
            return

        sinkName = sinkDock.get_name()
        sinkNode = sinkDock.get_node().procNode
        sourceName = sourceDock.get_name()
        sourceNode = sourceDock.get_node().procNode

        sinkPort = sinkNode.inputPorts[sinkName]
        sourcePort = sourceNode.outputPorts[sourceName]

        self.procNode.connectPorts(sourcePort, sinkPort)

    def __onSourceUnlink(self, sourceDock, sinkDock):
        sinkName = sinkDock.get_name()
        sinkNode = sinkDock.get_node().procNode
        sinkPort = sinkNode.inputPorts[sinkName]
        sourceName = sourceDock.get_name()
        sourceNode = sourceDock.get_node().procNode
        sourcePort = sourceNode.outputPorts[sourceName]
        self.procNode.disconnectPorts(sourcePort, sinkPort)

class FlowGui(object):
    def __init__(self, w, vbox):
        self.nv = GtkFlow.NodeView.new()
        self.nv.set_show_types(True)
        self.nodes = []
        vbox.pack_end(self.nv, True, True, 0)

    def createFlowNode(self, procNode):
        n = FlowGuiNode(procNode, self.nv) # TODO: remove dependency to nodeview
        self.nodes.append(n)
        self.nv.add_with_child(n, n.vbox)
        self.nv.set_node_position(n, procNode.guiPos[0], procNode.guiPos[1])


    def clear(self):
        for n in self.nodes:
            self.nv.remove_node(n)
        self.nodes = []


    def createFromProcGraph(self, procGraph):
        # create nodes
        for pn in procGraph.nodes:
            self.createFlowNode(pn)

        # update connections
        # TODO: this is really convoluted and requires many refs, find better way.
        for gn in self.nodes:
            gn.disableLinkingCb = True # TODO: disable handler directly?
            for portname, portobj in gn.procNode.outputPorts.items():
                for procSink in portobj.connectedTo:
                    guiSink = procSink.node.guiNode.portMap[procSink.name]
                    gn.portMap[portname].link(guiSink)

            gn.disableLinkingCb = False
