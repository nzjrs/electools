#!/usr/bin/env python
import optparse
import gtk
import logging
import brownout.Terminal as terminal

class UI:
    def __init__(self, echo, expander):
        w = gtk.Window()
        t = terminal.Terminal(
                echo=echo,
                expander=expander
        )

        w.set_title("Terminal")
        w.add(t)
        w.connect('delete-event', lambda *w: gtk.main_quit())
        w.show_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    u = UI(False, True)
    gtk.main()
