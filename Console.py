from Kernel import *
from EeekObject import *
import sys
import time

class Console(EeekObject):
    def __init__(self):
        EeekObject.__init__(self)

        self.buf  = []
        self.line = ""

    def input(self, char):
        if char == "|":
            pass
        elif char == "!":
            self.line = "Kernel.instance."
        elif char == "\x10":
            if len(self.buf)>1:
                self.line = self.buf[-2][2:]
        elif char == "\n":
            if self.line == "quit":
                Kernel.instance.send("\x1b\x1b#quit\ny        ")
                Kernel.instance.die("Quitted from console")
            if self.line == "save":
                Kernel.instance.send("\x1b\x1bSy      ")
                Kernel.instance.die("Saved from console")
            self.buf.append("> %s" % self.line)
            try:
                res = str(eval(self.line))
                if len(res) > 0:
                    self.buf.append(res)
                else:
                    self.buf.append("OK.")
            except:
                err = ",".join(map(str,sys.exc_info()))
                self.buf.append(err)
            self.line = ""
        elif char == '\x7f':
            self.line = self.line[:-1]
        else:
            self.line = self.line + char

    def draw(self):
        sys.stdout.write("\x1b[16;80H\x1b[1J\x1b[37m")

        sys.stdout.write("\x1b[16;1H")
        sys.stdout.write('-' * 80)
        sys.stdout.write("\x1b[1;1;H")

        printed = 1
        for line in self.buf[-14:]:
            sys.stdout.write(line)
            sys.stdout.write("\x1b[1E")

        sys.stdout.write("> %s" % self.line)

        sys.stdout.flush()

