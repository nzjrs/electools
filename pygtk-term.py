import gtk
import vte

import brownout.libserial as libserial
import brownout.RawEntry as rawentry
import brownout.HexView as hexview

class UI:
    def __init__(self):
        self.echo = True

        vb = gtk.VBox(spacing=4)
        vb.set_border_width(4)

        self.serial = libserial.SerialSender()
        sc = libserial.SerialChooser(self.serial)
        vb.pack_start(sc, expand=False, fill=False)

        self.term = vte.Terminal()
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

    def _on_entry_activate(self, entry):
        txt = entry.get_raw_text()

        if self.echo:
            self.term.feed(txt)
            if self.hv:
                self.hv.set_payload(txt)

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
    u = UI()
    gtk.main()
