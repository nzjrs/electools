# Serial port abstraction and config utilities
# 1/4/09

import gtk
import os.path
import serial
import logging

LOG = logging.getLogger('libserial')
DUMMY_PORT = "Select Serial Port"

class SerialChooser(gtk.HBox):
    """
    A composite Gtk widget containg a gtk.ComboBox
    that lists available serial ports, and a icon indicating
    whether the port is connected or not
    """
    def __init__(self, sender):
        gtk.HBox.__init__(self, spacing=2)
        
        self._sender = sender
        self._image = gtk.image_new_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)

        #populate the combo with available serial ports
        ports = [DUMMY_PORT] + self.get_ports()
        ports = self._build_combo(*ports)
        ports.connect("changed", self._on_serial_port_changed)

        #and available speeds
        speeds = self._build_combo(*self.get_speeds())
        speeds.connect("changed", self._on_serial_speed_changed)

        self.pack_start(self._image, False)
        self.pack_start(ports, expand=True)
        self.pack_start(speeds, expand=False)

    def _build_combo(self, *toModel):
        cb = gtk.ComboBox()
        store = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)
        for p in toModel:
            store.append( (p,) )
        cb.set_model(store)
        cb.set_active(0)
        return cb

    @staticmethod
    def get_ports():
        ports = [serial.device(i) for i in range(5)]
        if os.name == "posix":
            for device in ["/dev/ttyUSB%d" % i for i in range(5)]:
                if os.path.exists(device):
                    ports.append(device)
        return ports

    @staticmethod
    def get_speeds():
        return [9600, 19200, 38400, 57600, 115200]

    def _on_serial_port_changed(self, cb):
        port = cb.get_active_text()
        if port == DUMMY_PORT:
            self._sender.disconnect()
            self._image.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)
        else:
            if self._sender.connect(port=port):
                self._image.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
            else:
                self._image.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)

    def _on_serial_speed_changed(self, cb):
        speed = cb.get_active_text()
        if self._sender.connect(speed=int(speed)):
            self._image.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
        else:
            self._image.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)

class SerialSender:
    def __init__(self, port="/dev/null", speed=9600, timeout=1):
        self._serial = None
        self._port = port
        self._speed = speed
        self._timeout = timeout
        self._opened = False

    def is_open(self):
        return self._opened

    def connect(self, port=None, speed=None):
        """
        Opens the port
        """
        if port: p = port
        else: p = self._port
        if speed: s = speed
        else: s = self._speed

        #no-op if same port and speed is selected
        if (self._opened == False) or (s != self._speed) or (p != self._port):
            LOG.debug("Opening Port: %s @ %d" % (p,s))
            if self._serial and self._serial.isOpen():
                self._serial.close()
            try:
                self._serial = serial.Serial(p, s, timeout=self._timeout)
                self._serial.flushInput()
                self._port = p
                self._speed = s
                self._opened = self._serial.isOpen()
            except serial.SerialException:
                self._opened = False

        return self._opened

    def disconnect(self):
        if self._opened:
            self._serial.close()
            self._opened = False

    def read(self, *args, **kwargs):
        raise NotImplementedError

    def write(self, *args, **kwargs):
        raise NotImplementedError

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    p = SerialSender()
    w = gtk.Window()
    w.add(SerialChooser(p))
    w.show_all()
    gtk.main()

