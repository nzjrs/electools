#!/usr/bin/env python

import gobject
import gtk
import vte

import libserial
import libserial.SerialSender as SerialSender
import libserial.SerialChooser as SerialChooser

import RawEntry
import HexView

class Terminal(gtk.VBox):

    BACKSPACE = True
    DELETE = True

    def __init__(self, echo, expander, enable_tooltips):
        gtk.VBox.__init__(self, spacing=4)
        self._watch = None        
        self.echo = echo

        self.set_border_width(4)

        self.serial = SerialSender.SerialSender()
        self.serial.connect("serial-connected", self._on_serial_connected)
        sc = SerialChooser.SerialChooser(
                            sender=self.serial,
                            ports=libserial.get_ports(),
                            speeds=libserial.get_speeds())
        self.pack_start(sc, expand=False, fill=False)

        self.terminal = vte.Terminal()
        self.terminal.connect("commit", self._on_text_entered_in_terminal)
        self.pack_start(self.terminal, expand=True, fill=True)

        #tell vte to not get in the way of backspace/delete
        #
        #python-vte bindings don't appear to support this constant, 
        #so the magic values are being assumed from the C enum :/
        if self.BACKSPACE:
            #backbind = vte.ERASE_ASCII_BACKSPACE
            backbind = 2
        else:
            #backbind = vte.ERASE_AUTO_BACKSPACE
            backbind = 1

        if self.DELETE:
            #delbind = vte.ERASE_DELETE_SEQUENCE
            delbind = 3
        else:
            #delbind = vte.ERASE_AUTO
            delbind = 0
        self.terminal.set_backspace_binding (backbind)
        self.terminal.set_delete_binding (delbind)

        hb = gtk.HBox(spacing=2)
        self.pack_start(hb, expand=False, fill=True)

        entry = RawEntry.MyEntry(enable_tooltips)
        entry.connect("activate", self._on_entry_activate)
        hb.pack_start(entry, expand=True, fill=True)

        lbl = gtk.Label("0")
        lbl.set_width_chars(4)
        lbl.set_justify(gtk.JUSTIFY_RIGHT)
        hb.pack_start(lbl, expand=False, fill=False)

        if enable_tooltips:
            lbl.props.has_tooltip = True
            lbl.connect("query-tooltip", self._on_lbl_tooltip)

        entry.connect("changed", self._on_entry_changed, lbl)

        #store the hex view in an expander
        #only create said viewwhen revealed the first time
        if expander:
            exp = gtk.expander_new_with_mnemonic("_Hex View")
            exp.connect("notify::expanded", self._expander_callback)
            self.pack_start(exp, expand=False, fill=False)
        self.hexview = None
        self._hexbuf = ""

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
        #remove the old watch
        if self._watch:
            gobject.source_remove(self._watch)

        if connected:
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

    def _on_entry_changed(self, entry, lbl):
        lbl.set_text(str(entry.get_length()))

    def _on_lbl_tooltip(self, widget, x, y, keyboard_tip, tooltip):
        if keyboard_tip:
            return False

        tooltip.set_text("%s bytes" % widget.get_text())
        return True

    def _on_entry_activate(self, entry):
        self._send_text(entry.get_raw_text())

    def _expander_callback(self, expander, *args):
        if expander.get_expanded():
            if not self.hexview:
                self.hexview = HexView.HexView()
                self.hexview.set_border_width(0)
                expander.add(self.hexview)
            expander.show_all()
        else:
            expander.remove(self.hexview)
            self.hexview = None

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    w = gtk.Window()
    t = Terminal(False, True)


    w.connect('delete-event', lambda *w: gtk.main_quit())
    w.add(t)
    w.show_all()
    gtk.main()
