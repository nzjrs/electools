import os.path
import subprocess
import tempfile
import logging

LOG = logging.getLogger('compiler')
HARDWARE_DIR = "/home/john/Programming/electools.git/data/hardware/"

class Compiler:
    def __init__(self, board, sketch):
        self._board = board
        self._sketchfile = os.path.abspath(sketch)
        self._builddir = tempfile.mkdtemp()

    def _get_include_paths(self, source):
        return [
            os.path.dirname(self._sketchfile),
            os.path.join(HARDWARE_DIR, "cores", self._board["build"]["core"])
        ]

    def get_version(self):
        return subprocess.Popen(["avr-gcc", "-dumpversion"], stdout=subprocess.PIPE).communicate()[0].strip()

    def _compile_source(self, source):
        src = os.path.abspath(source)
        out = os.path.join(self._builddir,os.path.basename(src)) + ".o"

        if src.endswith(".c"):
            cmd = ["avr-gcc"]
        else:
            cmd = ["avr-g++"]

        cmd += ["-c", "-g", "-Os", "-w", "-ffunction-sections", "-fdata-sections"]
        cmd += ["-mmcu=" + self._board["build"]["mcu"]]
        cmd += ["-DF_CPU=" + self._board["build"]["f_cpu"]]
        cmd += ["-I%s" % p for p in self._get_include_paths(src)]
        cmd += [src]
        cmd += ["-o" + out]

        LOG.debug(" ".join(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode == 0:
            return out
        else:
            LOG.warn(stderr)
            return None

    def _create_archive(self, objects):
        lib = os.path.join(self._builddir, "core.a")
        for o in objects:
            cmd = ["avr-ar", "rcs", lib, o]
            LOG.debug(" ".join(cmd))
            
            if subprocess.Popen(["avr-ar", "rcs", lib, o], stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait() != 0:
                return None

        return lib


    def _link_objects(self, mainobj, lib):
        cmd = ["avr-gcc", "-Os", "-Wl,--gc-sections"]
        cmd += ["-mmcu=" + self._board["build"]["mcu"]]
        cmd += ["-o" + os.path.splitext(self._sketchfile)[0] + ".elf"]
        cmd += [mainobj]
        cmd += [lib]
        cmd += ["-L" + self._builddir]
        cmd += ["-lm"]

        LOG.debug(" ".join(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        return p.returncode == 0

    def compile_me(self, main, sources):
        objects = [self._compile_source(s) for s in sources]
        if None in objects:
            LOG.warn("Compile failed")
            return False

        lib = self._create_archive(objects)
        if not lib:
            LOG.warn("Create library failed")
            return False

        mainobj = self._compile_source(main)
        if not mainobj:
            LOG.warn("Compile application failed")
            return False

        if not self._link_objects(mainobj, lib):
            LOG.warn("Link failed")
            return False

        return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    c = Compiler(
            board={"build":{"mcu":"atmega8","f_cpu":"4000000", "core":"arduino"}},
            sketch="123.pde")

    a = [
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring_serial.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring_digital.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/WInterrupts.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring_analog.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring_pulse.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/pins_arduino.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/wiring_shift.c",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/WMath.cpp",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/HardwareSerial.cpp",
        "/home/john/Desktop/arduino-read-only/build/linux/work/hardware/cores/arduino/Print.cpp"
    ]
    c.compile_me("/home/john/Programming/electools.git/test/testmain.cpp", a)

