import os.path

class Compiler:
    def __init__(self):
        pass

    def _get_compiler_arguments(self):
        return [
            "-c",                   #compile, don't link
            "-g",                   #include debugging info (so errors include line numbers)
            "-Os",                  #optimize for size
            "-w",                   #surpress all warnings
            "-ffunction-sections",  #place each function in its own section
            "-fdata-sections",      #
            "-mmcu=",               # + Preferences.get("boards." + Preferences.get("board") + ".build.mcu"),
            "-DF_CPU=",             # + Preferences.get("boards." + Preferences.get("board") + ".build.f_cpu"),
        ]

    def _get_include_paths(self):
        return ["."]

    def compile_source(self, source):
        base = ["avr-gcc"]
        base += self._get_compiler_arguments()
        base += ["-I%s" % p for p in self._get_include_paths()]
        base += ["%s" % os.path.abspath(source)]
        base += ["-o %s" % os.path.abspath(source)]

        print base

    def link_objects(self, objects):
        base = [
            "avr-gcc",
            "-Os",
            "-Wl,--gc-sections",
            "-mmcu=",               # + Preferences.get("boards." + Preferences.get("board") + ".build.mcu"),
            "-o",                   #buildPath + File.separator + sketch.name + ".elf"
        ]
        base += []


if __name__ == "__main__":
    c = Compiler()
    c.compile_source("test.c")
