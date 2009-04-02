#!/usr/bin/env python
import gtk
import logging
import brownout.Terminal as terminal

class UI:
    def __init__(self, echo=False, expander=True):
        w = gtk.Window()
        w.set_title("Terminal")
        w.add(terminal.Terminal())
        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    u = UI()
    gtk.main()
