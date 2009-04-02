#!/usr/bin/env python

import gobject
import gtk
import vte

import logging

import brownout.libserial as libserial
import brownout.RawEntry as rawentry
import brownout.HexView as hexview

class UI:
    def __init__(self):
        self.echo = False
        self.watch = None        

        vb = gtk.VBox(spacing=4)
        vb.set_border_width(4)

        self.serial = libserial.SerialSender()
        self.serial.connect("serial-connected", self._on_serial_connected)
        sc = libserial.SerialChooser(self.serial)
        vb.pack_start(sc, expand=False, fill=False)

        self.term = vte.Terminal()
        self.term.connect("commit", self._on_text_entered_in_terminal)
        vb.pack_start(self.term, expand=True, fill=True)

        entry = rawentry.MyEntry()
        entry.connect("activate", self._on_entry_activate)
        vb.pack_start(entry, expand=False, fill=False)

        #store the hex view in an expander, only create said view
        #when revealed the first time
        expander = gtk.expander_new_with_mnemonic("_Hex View")
        expander.connect("notify::expanded", self._expander_callback)
        vb.pack_start(expander, expand=False, fill=False)
        self.hv = None

        w = gtk.Window()
        w.add(vb)
        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

    def _send_text(self, txt):
        if self.echo:
            self.term.feed(txt)
            if self.hv:
                self.hv.set_payload(txt)
        self.serial.get_serial().write(txt)

    def _on_serial_connected(self, serial, connected):
        if connected:
            #remove the old watch
            if self.watch:
                gobject.source_remove(self.watch)

            #add new watch
            self.watch = gobject.io_add_watch(
                            serial.get_serial().fileno(), 
                            gobject.IO_IN | gobject.IO_PRI,
                            self._on_serial_data_available,
                            priority=gobject.PRIORITY_HIGH
            )

    def _on_serial_data_available(self, fd, condition):
        dat = self.serial.get_serial().read()
        self.term.feed(dat)
        if self.hv:
            self.hv.set_payload(dat)
        return True

    def _on_text_entered_in_terminal(self, term, txt, length):
        self._send_text(txt)

    def _on_entry_activate(self, entry):
        self._send_text(entry.get_raw_text())

    def _expander_callback(self, expander, *args):
        if expander.get_expanded():
            if not self.hv:
                self.hv = hexview.HexView()
                self.hv.set_border_width(0)
                expander.add(self.hv)
            expander.show_all()
        else:
            self.hv.hide_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    u = UI()
    gtk.main()
