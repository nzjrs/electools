import os.path
import sys
import gtk
import gtksourceview2 as gtksourceview
import gio
import pango
import logging

LOG = logging.getLogger('compiler')

class Editor(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        self._b = gtksourceview.Buffer()
        style_scheme = gtksourceview.style_scheme_manager_get_default().get_scheme('classic')
        if style_scheme:
            self._b.set_style_scheme(style_scheme)
        self._b.set_language(gtksourceview.language_manager_get_default().get_language("cpp"))
        self._b.set_highlight_syntax(True)

        #self._b.connect('mark-set', move_cursor_cb, view)
        #self._b.connect('changed', update_cursor_position, view)

        self._v = gtksourceview.View(self._b)
        self._v.set_show_line_numbers(True)
        #self._v.set_show_line_marks(action.get_active())
        #self._v.set_show_right_margin(action.get_active())
        #self._v.set_auto_indent(action.get_active())
        #self._v.set_insert_spaces_instead_of_tabs(action.get_active())
        #self._v.set_tab_width(action.get_current_value())
        #self._v.connect('button-press-event', button_press_cb)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_IN)
        self.pack_start(sw, True, True, 0)
        sw.add(self._v)

        # setup view
        font_desc = pango.FontDescription('monospace')
        if font_desc:
            self._v.modify_font(font_desc)

    def open_file(self, path):
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            LOG.warn("Could not find %s", path)
            return False

        self._b.begin_not_undoable_action()
        # TODO: use g_io_channel when pygtk supports it
        try:
            txt = open(path).read()
        except:
            return False
        self._b.set_text(txt)
        self._b.set_data('filename', path)
        self._b.end_not_undoable_action()

        self._b.set_modified(False)
        self._b.place_cursor(self._b.get_start_iter())

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    e = Editor()
    e.open_file("data/testmain.cpp")

    w = gtk.Window()
    w.connect('delete-event', lambda *w: gtk.main_quit())
    w.set_default_size(500, 500)
    w.add(e)
    w.show_all()

    gtk.main()

