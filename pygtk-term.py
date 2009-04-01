import gtk
import vte

import brownout.libserial as libserial
import brownout.RawEntry as rawentry
import brownout.HexView as hexview

class UI:
    def __init__(self):
        w = gtk.Window()
        vb = gtk.VBox()
        w.add(vb)

        serial = libserial.SerialSender()
        sc = libserial.SerialChooser(serial)
        vb.pack_start(sc, expand=False, fill=False)

        term = vte.Terminal()
        vb.pack_start(term, expand=True, fill=True)

        entry = rawentry.MyEntry()
        vb.pack_start(entry, expand=False, fill=False)

        #store the hex view in an expander, only create said view
        #when revealed the first time
        expander = gtk.expander_new_with_mnemonic("_Hex View")
        expander.connect("notify::expanded", self._expander_callback)
        vb.pack_start(expander, expand=False, fill=False)
        self.hv = None

        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

    def _expander_callback(self, expander, *args):
        if expander.get_expanded():
            if not self.hv:
                self.hv = hexview.HexView()
                expander.add(self.hv)
            expander.show_all()
        else:
            self.hv.hide_all()

if __name__ == "__main__":
    u = UI()
    gtk.main()