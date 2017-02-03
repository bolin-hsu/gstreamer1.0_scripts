#!/usr/bin/env python
import thread
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject

class CLI_Main(object):
    def __init__(self):
        self.player = Gst.Pipeline.new('level')
        source = Gst.ElementFactory.make("alsasrc", "alsasrc")
        level = Gst.ElementFactory.make('level', 'level')
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        source.set_property('device', 'hw:0,0,0')

        self.level = level

        self.player.add(source)
        self.player.add(level)
        self.player.add(fakesink)
        source.link(level)
        level.link(fakesink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ELEMENT:
            s = message.get_structure()
            if s.get_name() == 'level':
                for pad in self.level.srcpads:
                    if pad.has_current_caps():
                        print 'caps', pad.get_current_caps().to_string()
                print 'rms', s.get_value('rms'), s.get_value('peak')
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playmode = False

    def start(self):
        self.player.set_state(Gst.State.PLAYING)

GObject.threads_init()
Gst.init(None)
mainclass = CLI_Main()
thread.start_new_thread(mainclass.start, ())
loop = GLib.MainLoop()
loop.run()
