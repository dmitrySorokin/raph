#!/usr/bin/python
import sys

from curses import *

from myconstants import *
from NethackSock import *
from FramebufferParser import *
from SocketLogger import *
from DGLParser import *
from Personality import *
from Senses import *
from Console import *
from Hero import *
from Dungeon import *
from MonsterSpoiler import *
from Pathing import *
from TestBrain import *
from Cursor import *
from ItemDB import *
from Inventory import *

class Eeek:
    def __init__(self):
        self.mode = MODE_COMMANDS # Other is MODE_USERPLAY where you are in control of the hero

        if CURSES:
            # Initialize curses
            cbreak()
            noecho()

        # Initialize the Kernel
        Kernel()

        # Set's up the socket
        NethackSock()

        # Socket observers
        SocketLogger() # This should be before other stuff for easier debugging
        FramebufferParser()
        DGLParser()

        # Stuff 
        Console()
        Cursor()
        Dungeon()
        Hero()
        MonsterSpoiler()
        ItemDB()
        Inventory()

        # AI
        Personality()
        Senses()
        Pathing()

        # Brains
        curBrain = TestBrain()

        Kernel.instance.Personality.setBrain(curBrain) # Default brain

    def connect(self, server, port):
        Kernel.instance.NethackSock.connect(server, port)
        Kernel.instance.NethackSock.start()

    def run(self):
        # User input
        try:
            while not Kernel.instance.NethackSock.done:
                if CURSES:
                    input = chr(stdscr.getch())

                    if input == '/' and self.mode not in [MODE_CONSOLE, MODE_CURSOR]:
                        if Kernel.instance.Hero.y != None and Kernel.instance.Hero.x != None:
                            Kernel.instance.log("Starting cursor")
                            Kernel.instance.Cursor.start()

                            self.mode = MODE_CURSOR

                            Kernel.instance.Cursor.was = Kernel.instance.paused()
                            Kernel.instance.setPause(True)
                            Kernel.instance.Cursor.draw()
                            continue
                    elif input in ['~', '|'] and self.mode not in [MODE_CONSOLE, MODE_CURSOR]:
                        Kernel.instance.log("Opening console")

                        self.mode = MODE_CONSOLE
                        Kernel.instance.Console.was = Kernel.instance.paused()
                        Kernel.instance.setPause(True)
                        Kernel.instance.Console.draw()

                    elif self.mode == MODE_CURSOR:
                        if input == '/':
                            Kernel.instance.log("Stopping cursor")
                            self.mode = MODE_COMMANDS
                            Kernel.instance.setPause(Kernel.instance.Cursor.was)
                            continue
                        else:
                            Kernel.instance.Cursor.input(input)
                            Kernel.instance.Cursor.draw()


                    elif self.mode == MODE_CONSOLE:
                        if input in ['~', '|']:
                            Kernel.instance.log("Closing console")
                            self.mode = MODE_COMMANDS
                            Kernel.instance.setPause(Kernel.instance.Console.was)
                        else:
                            Kernel.instance.Console.input(input)
                            Kernel.instance.Console.draw()

                    elif self.mode == MODE_USERPLAY:
                        if input == '-':
                            Kernel.instance.log("Enering commands-mode")
                            self.mode = MODE_COMMANDS
                        else:
                            Kernel.instance.send(input)

                    elif self.mode == MODE_COMMANDS:
                        if input == ';':
                            Kernel.instance.log(str(Kernel.instance.curTile()))
                        elif input == 'u':
                            if not Kernel.instance.paused():
                                Kernel.instance.setPause(True)
                            else:
                                Kernel.instance.setPause(False)
                        elif input == 'p':
                            Kernel.instance.log("Entering userplay-mode")
                            self.mode = MODE_USERPLAY

        except KeyboardInterrupt:
            self.die("Ctrl+C")
        except:
            err = ",".join(map(str,sys.exc_info()))
            self.die(msg=err)
        self.die()

    def die(self, msg='No quitmsg'):
        Kernel.instance.NethackSock.send("Sy      ")
        Kernel.instance.NethackSock.done = True
        if CURSES:
            endwin()
        Kernel.instance.die("Died from Eeek:%s" % msg)
