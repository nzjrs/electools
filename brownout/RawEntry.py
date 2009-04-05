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
    def __init__(self, val, chunk):
        self._val = val
        self._chunk = chunk
    def as_string(self):
        return chr(self._val)
    def as_markup(self):
        return '<span underline="single" underline_color="%s">%s</span>' % (self.color, self._chunk)
    is_number = True
    length = 1
    color = ""

CHAR_REPLACE = {
    "\\t"   :   "\t",
    "\\a"   :   "\a",
    "\\b"   :   "\b",
    "\\f"   :   "\f",
    "\\n"   :   "\n",
    "\\r"   :   "\r",
    "\\t"   :   "\t",
    "\\v"   :   "\v"
}

class _Char(_Number):
    color = "green"

class _Hex(_Number):
    color = "red"

class _Int(_Number):
    color = "blue"

class _Binary(_Number):
    color = "yellow"

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

    def _get_value(self, chunk):
        print "###", chunk

        #check for space
        if chunk == '':
            return _String(' ')

        if len(chunk) > 2:
            #try binary
            if chunk[0:2] == "0b":
                try:
                    val = int(chunk[2:], 2)
                    if val <= 0xFF:
                        return _Binary(val, chunk)
                except ValueError: pass
            #try hex
            if chunk[0:2] == "0x":
                try:
                    val = int(chunk[2:], 16)
                    if val <= 0xFF:
                        return _Hex(val, chunk)
                except ValueError: pass

        #try integer
        if len(chunk) > 1 and chunk[0] == "#":
            try:
                val = int(chunk[1:], 10)
                if val <= 0xFF:
                    return _Int(val, chunk)
            except ValueError: pass

        #try char
        if len(chunk) == 2 and chunk in CHAR_REPLACE:
            return _Char(CHAR_REPLACE[chunk], chunk)

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

    def get_length(self):
        return self._length

    def get_raw_text(self):
        if self._hasnumber:
            return "".join([v.as_string() for v in self._values])
        else:
            return " ".join([v.as_string() for v in self._values])

if __name__ == "__main__":
    w = gtk.Window()
    w.add(MyEntry())
    w.show_all()
    gtk.main()
