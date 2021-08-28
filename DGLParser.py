from Kernel import *
from EeekObject import *
from SocketObserver import *

STATE_NOT_LOGGEDIN   = 0
STATE_AUTHENTICATE   = 1
STATE_LOGGEDIN       = 2
STATE_INIT_PLAYER    = 3
STATE_PLAYING        = 4

class DGLParser(SocketObserver, EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        SocketObserver.__init__(self)

        self.dgl_line  = ["\x08\x08## dgamelaunch 1.4.8 - network console game launcher","Welcome to nethack.fribyte.uib.no"]
        self.play_line = ["p) Play NetHack", "p) Play"]
        self.quit_line = ["q) Quit"]
        self.pick_line = ["Shall I pick a character's race, role, gender and alignment for you? [ynq]"]
        self.more_line = "--More--"
        self.state = STATE_NOT_LOGGEDIN

        Kernel.instance.log("Setting state to STATE_NOT_LOGGEDIN")

    def parse(self, msg):
        # Not logged in
        if self.state == STATE_NOT_LOGGEDIN:
            for line in self.dgl_line:
                if msg.find(line) >= 0:
                    Kernel.instance.log("Logging in ..")
                    Kernel.instance.send("l\rnewrlbot\rsber1scool\r")
                    self.state = STATE_AUTHENTICATE
        #Authenticate OK?
        if self.state == STATE_AUTHENTICATE:
            for line in self.play_line:
                if msg.find(line) >= 0:
                    Kernel.instance.log("Logged in. Starting game ..")
                    Kernel.instance.send("p")
                    self.state = STATE_INIT_PLAYER
        #Authenticate OK! Let's start.
        if self.state == STATE_INIT_PLAYER:
            for line in self.pick_line:
                if msg.find(line) >= 0:
                    Kernel.instance.log("No current games, starting one ..")
                    Kernel.instance.send("nvhn")

                    Kernel.instance.NethackSock.s.recv(9999)
                    Kernel.instance.send("\x12")

                    Kernel.instance.sendSignal("game_start")
                    self.state = STATE_PLAYING
                elif msg.find(self.more_line) >= 0:
                    Kernel.instance.send(" ")

                    Kernel.instance.sendSignal("game_start")
                    self.state = STATE_PLAYING
                elif msg.find("[yn]") >= 0:
                    Kernel.instance.send("y")
