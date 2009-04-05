import UserDict

class DotDict(UserDict.IterableUserDict):
    def __init__(self):
        UserDict.IterableUserDict.__init__(self)

    def __setitem__(self, key, val):
        bits = key.split(".")

        if bits[0] not in self.data:
            self.data[bits[0]] = {}

        #lilypad.name
        if len(bits) == 2:
            self.data[bits[0]][bits[1]] = val
        #lilypad.upload.protocol
        elif len(bits) == 3:
            if bits[1] not in self.data[bits[0]]:
                self.data[bits[0]][bits[1]] = {}
            self.data[bits[0]][bits[1]][bits[2]] = val

if __name__ == "__main__":
    d = DotDict()
    d["lilypad.upload.protocol"] = "stk500"
    d["lilypad.upload.maximum_size"]=14336
    d["lilypad.name"]="LilyPad Arduino"
    print d.data
    print d["lilypad"]["upload"]["maximum_size"]
