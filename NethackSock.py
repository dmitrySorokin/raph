from Kernel import *
from threading import *
from socket import *
from EeekObject import *
import sys
import time

class NethackSock(Thread, EeekObject):
    def __init__(self):
        EeekObject.__init__(self)
        Thread.__init__(self)

        self.done = False
        self.s = socket(AF_INET, SOCK_STREAM)

        self.paused = False

    def connect(self, host, port):
        self.s.connect((host, port))
        self.s.send("\xFF\xFB\x18\xFF\xFA\x18\x00xterm-color\xFF\xF0\xFF\xFC\x20\xFF\xFC\x23\xFF\xFC\x27\xFF\xFE\x03\xFF\xFB\x01\xFF\xFD\x05\xFF\xFB\x21\xFF\xFB\x1F\xFF\xFA\x1F\x00\x50\x00\x18\xFF\xF0")
        time.sleep(0.1)
        self.s.send("l")
        time.sleep(0.1)
        self.s.send("newrlbot\n")
        time.sleep(0.1)
        self.s.send("sber1scool\n")
        time.sleep(0.1)
        self.s.send("p\n")
        time.sleep(0.1)
        self.s.send("y\n")
        time.sleep(0.1)
        self.s.send("\n")
        time.sleep(0.1)
        Kernel.instance.sendSignal("game_start")


    def send(self, msg):
        return self.s.send(msg)

    def die(self):
        self.done = True

    def run(self):
        while not self.done:
            if self.paused:
                time.sleep(0.1)
                continue

            buf = ""
            if Kernel.instance.FramebufferParser.gameStarted:
                self.s.send("\xff\xfdc")
                while not buf.endswith("\xff\xfcc"):
                    buf = buf + self.s.recv(9999)
            else:
                buf = self.s.recv(9999)
            Kernel.instance.sockRecv(buf)
