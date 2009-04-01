import gtk
import glib
import pango

class _String:
    def __init__(self, val):
        self._val = val
    def as_string(self):
        return self._val
    def as_markup(self):
        return '<span underline="single" underline_color="green">%s</span>' % glib.markup_escape_text(self._val)
    def get_len(self):
        return len(self._val)
    is_number = False
    length = property(get_len)

class _Number:
    def __init__(self, val):
        self._val = val
    is_number = True
    length = 1

class _Space(_Number):
    def as_string(self):
        return ' '
    def as_markup(self):
        return '<span underline="single" underline_color="green"> </span>'
    is_number = False

class _Char(_Number):
    REPLACE = {
        "\\t"   :   "\t",
        "\\a"   :   "\a",
        "\\b"   :   "\b",
        "\\f"   :   "\f",
        "\\n"   :   "\n",
        "\\r"   :   "\r",
        "\\t"   :   "\t",
        "\\v"   :   "\v"
    }
    def as_string(self):
        return _Char.REPLACE[self._val]
    def as_markup(self):
        return '<span underline="single" underline_color="green">%s</span>' % self._val

class _Hex(_Number):
    def as_string(self):
        return chr(self._val)
    def as_markup(self):
        return '<span underline="single" underline_color="red">0x%X</span>' % self._val

class _Int(_Number):
    def as_string(self):
        return chr(self._val)
    def as_markup(self):
        return '<span underline="single" underline_color="blue">#%d</span>' % self._val

class MyEntry(gtk.Entry):
    def __init__(self):
        gtk.Entry.__init__(self)

        self._length = 0
        self._hasnumber = False
        self._values = []
        self._markup = ""
        self._font = pango.FontDescription("Mono 12")

        self.connect("changed", self._on_change)
        self.connect("expose-event", self._on_expose)
        self.connect("activate", self._on_activate)

    def _get_value(self, chunk):
        print "###", chunk

        #check for space
        if chunk == '':
            return _Space(chunk)

        #try hex
        if len(chunk) > 2:
            try:
                val = int(chunk, 16)
                if val <= 0xFF:
                    return _Hex(val)
            except ValueError: pass

        #try integer
        if len(chunk) > 1:
            try:
                val = int(chunk[1:], 10)
                if val <= 0xFF:
                    return _Int(val)
            except ValueError: pass

        #try char
        if len(chunk) == 2 and chunk in _Char.REPLACE:
            return _Char(chunk)

        #else it is a string
        return _String(chunk)

    def _on_change(self, *args):
        text = self.get_text()
        markup = ""
        
        self._length = 0
        self._hasnumber = False
        self._values = [self._get_value(chunk) for chunk in text.split(' ')]
        for val in self._values:
            markup += val.as_markup()
            markup += ' '
            self._hasnumber |= val.is_number
            self._length += val.length

        if self._hasnumber:
            self._markup = markup
        else:
            self._markup = glib.markup_escape_text(text)
            self._length = len(text)

        self.get_layout().set_markup(self._markup)

    def _on_expose(self, *args):
        self.get_layout().set_markup(self._markup)
        self.get_layout().set_font_description(self._font)

    def _on_activate(self, *args):
        if self._hasnumber:
            txt = "".join([v.as_string() for v in self._values])
        else:
            txt = " ".join([v.as_string() for v in self._values])

        print "%s:\t%s" % (self._length, txt)

if __name__ == "__main__":
    w = gtk.Window()
    w.add(MyEntry())
    w.show_all()
    gtk.main()
