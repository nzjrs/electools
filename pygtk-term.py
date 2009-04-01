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

        hv = hexview.HexView()
        vb.pack_start(hv, expand=False, fill=False)

        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

if __name__ == "__main__":
    u = UI()
    gtk.main()
