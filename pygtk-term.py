#!/usr/bin/env python

import gobject
import gtk
import vte

import logging

import brownout.libserial as libserial
import brownout.RawEntry as rawentry
import brownout.HexView as hexview

class UI:
    def __init__(self, echo=False, expander=True):
        self._watch = None        
        self.echo = False

        vb = gtk.VBox(spacing=4)
        vb.set_border_width(4)

        self.serial = libserial.SerialSender()
        self.serial.connect("serial-connected", self._on_serial_connected)
        sc = libserial.SerialChooser(self.serial)
        vb.pack_start(sc, expand=False, fill=False)

        self.terminal = vte.Terminal()
        self.terminal.connect("commit", self._on_text_entered_in_terminal)
        vb.pack_start(self.terminal, expand=True, fill=True)

        entry = rawentry.MyEntry()
        entry.connect("activate", self._on_entry_activate)
        vb.pack_start(entry, expand=False, fill=False)

        #store the hex view in an expander
        #only create said viewwhen revealed the first time
        if expander:
            exp = gtk.expander_new_with_mnemonic("_Hex View")
            exp.connect("notify::expanded", self._expander_callback)
            vb.pack_start(exp, expand=False, fill=False)
        self.hexview = None
        self._hexbuf = ""

        w = gtk.Window()
        w.add(vb)
        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

    def _show_text(self, txt):
        self.terminal.feed(txt)
        if self.hexview:
            if len(txt) + len(self._hexbuf) > 80:
                self._hexbuf = txt
            else:
                self._hexbuf += txt
            self.hexview.set_payload(self._hexbuf)


    def _send_text(self, txt):
        if self.echo:
            self._show_text(txt)
        ser = self.serial.get_serial()
        if ser:
            ser.write(txt)

    def _on_serial_connected(self, serial, connected):
        if connected:
            #remove the old watch
            if self._watch:
                gobject.source_remove(self._watch)

            #add new watch
            self._watch = gobject.io_add_watch(
                            serial.get_serial().fileno(), 
                            gobject.IO_IN | gobject.IO_PRI,
                            self._on_serial_data_available,
                            priority=gobject.PRIORITY_HIGH
            )

    def _on_serial_data_available(self, fd, condition):
        self._show_text(self.serial.get_serial().read())
        return True

    def _on_text_entered_in_terminal(self, term, txt, length):
        self._send_text(txt)

    def _on_entry_activate(self, entry):
        self._send_text(entry.get_raw_text())

    def _expander_callback(self, expander, *args):
        if expander.get_expanded():
            if not self.hexview:
                self.hexview = hexview.HexView()
                self.hexview.set_border_width(0)
                expander.add(self.hexview)
            expander.show_all()
        else:
            expander.remove(self.hexview)
            self.hexview = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    u = UI()
    gtk.main()
