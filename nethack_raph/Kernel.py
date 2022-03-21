from nethack_raph.myconstants import TTY_WIDTH, TTY_HEIGHT, TTY_BRIGHT, DUNGEON_WIDTH
from nethack_raph.Senses import Senses
from nethack_raph.Hero import Hero
from nethack_raph.Dungeon import Dungeon
from nethack_raph.TestBrain import TestBrain
from nethack_raph.Inventory import Inventory

import re
import sys
import numpy as np
import weakref


def render(chrs, cols, offset=(1, 1)):
    # begin by saving the current cursor, whatever it is
    ansi = '\033[s'

    # render output line by line with ANSI escapes
    height, width = chrs.shape
    L0, C0 = offset
    for L in range(height):
        # position the cursor at (L, C) with \033[<L>;<C>H 1-based
        ansi += f'\033[{L0 + L:d};{C0:d}H'
        for C in range(width):
            # set fg color with \033[<bold?>;3<3-bit color>m
            cl, ch = cols[L, C], chrs[L, C]
            ansi += f'\033[{bool(cl & 8):1d};3{cl & 7:1d}m{ch:c}'

    # flush after the final line, restore the cursor and reset the color
    ansi += f'\033[{height+1};0H\033[u\033[m'

    return ansi


class Kernel:
    def __init__(self, verbose, early_stop=np.inf):
        self._file = None
        self._frames_log = None
        self.verbose = False
        self.early_stop = early_stop
        self.set_verbose(verbose)

        # Stuff
        self.dungeon = Dungeon(weakref.ref(self))
        self.hero = Hero(weakref.ref(self))
        self.inventory = Inventory(weakref.ref(self))

        # AI
        self.senses = Senses(weakref.ref(self))

        # Brains
        self.brain = TestBrain(weakref.ref(self))

        self.stdout("\u001b[2J\u001b[0;0H")
        self.action = ''
        self.state = None
        self.bot = None
        self.top = None
        self.tty_chars = None

        self.steps = 0
        self.last_turn_update = 0

    def set_verbose(self, value):
        if not self.verbose and value:
            from pathlib import Path
            Path("logs").mkdir(parents=True, exist_ok=True)
            self._file = open("logs/log.txt", "w")
            self._frames_log = open("logs/frames.txt", "w")
        self.verbose = value

    def curLevel(self):
        return self.dungeon.curBranch.curLevel

    def curTile(self):
        return self.dungeon.curBranch.curLevel.tiles[self.hero.x, self.hero.y]

    def searchBot(self, regex):
        return re.search(regex, self.bot)

    def searchTop(self, regex):
        return re.search(regex, self.top)

    def top_line(self):
        return self.top

    def bot_line(self):
        return self.bot

    def get_row_line(self, row):
        if row < 0 or row > 24:
            return ""
        return self.tty_chars[row * TTY_WIDTH: (row + 1) * TTY_WIDTH]

    def update(self, obs):
        assert len(self.action) == 0

        self.steps += 1

        if self.steps == 1:  # parsing agent's attributes at the start
            self.send('\x18')  # ctrl + x = player info
            return self.action

        self.state = np.zeros((2, TTY_HEIGHT, TTY_WIDTH), dtype=np.uint8)
        self.state[0] = obs['tty_chars']
        self.state[1] = obs['tty_colors']
        self.top = bytes(obs['message'][obs['message'].nonzero()]).decode('ascii')

        # extract the the bottom lines
        self.tty_chars = bytes(obs['tty_chars']).decode('ascii')  # flattens 24x80
        self.bot = self.tty_chars[22 * TTY_WIDTH:]

        if self.verbose:
            self.stdout(render(*self.state))
            self.log_screen(chars=self.state[0], log=self._frames_log,
                            coords=(obs['blstats'][1], obs['blstats'][0]))

        self.log(f"\n ------------------ STEP {self.steps} ------------------ ")
        if self.hero.turns != obs['blstats'][20]:
            self.last_turn_update = self.steps

        if self.steps - self.last_turn_update > 30:
            self.log("Looks like we're stuck in some kind of loop")
            self.action = '\x1b10s'  # ESC + waiting 10 turns
            return self.action

        self.log("--------- HERO ---------")
        self.hero.update(obs['blstats'], self.top, self.bot)
        assert len(self.action) == 0

        if self.hero.score > self.early_stop:
            self.die(f'score = {self.hero.score}')
            return self.action

        self.log("-------- INVENTORY -------- ")
        self.inventory.update(obs)
        assert len(self.action) == 0

        self.log("--------- DUNGEON ---------")
        self.dungeon.dlvl = obs['blstats'][12]
        self.dungeon.update(bytes(obs['chars']).decode('ascii'), obs['glyphs'])
        assert len(self.action) == 0

        # this checks for a foreground overlay message
        if obs['misc'][2]:
            self.log("--------- MENU --------- ")
            self.senses.parse_menu()

        self.log("--------- SENSES --------- ")
        self.senses.update()

        self.log("-------- MESSAGES -------- ")
        self.senses.parse_messages()

        return self.action

    def step(self, obs):
        self.update(obs)
        if self.action:
            return self.action

        self.curBrain.execute_next(self.curLevel())
        return self.action

    def send(self, line):
        self.action = self.action + line

    def log(self, str):
        if self.verbose:
            self._file.write("%s"%str+"\n")
            self._file.flush()

    def die(self, msg):
        if self.verbose:
            self.stdout("\x1b[35m\x1b[3;1H%s\x1b[m\x1b[25;0f" % msg)
            self.log(msg)
        self.action = '#quit\ry'

    def drawString(self, msg):
        if self.verbose:
            self.log("Currently -> "+msg)
            self.stdout("\x1b[35m\x1b[25;0H%s\x1b[m" % msg + " "*(240-len(msg)))

    def addch(self, y, x, char, c=None):
        if self.verbose:
            self.stdout("%s\x1b[%d;%dH%s\x1b[m" % (c and "\x1b[%dm" % c or "", y, x, char))

    def draw_path(self, path, color=41):
        if self.verbose:
            for tile in path:
                self.stdout("\x1b[%dm\x1b[%d;%dH%s\x1b[m" % (color, tile[0] + 2, tile[1] + 1, 'X'))

    def log_screen(self, chars, log, coords):
        if not self.verbose:
            return

        for row in chars:
            log.write("\n")
            for ch in row:
                log.write(chr(ch))
        if self.dungeon.curBranch:
            log.write(str(coords))
        log.flush()

    def stdout(self, msg):
        if self.verbose:
            sys.stdout.write(msg)
            sys.stdout.flush()

    def __del__(self):
        hero = self.hero
        self.log(f"Episode stats: {hero.role}-{hero.race}-{hero.moral}-{hero.gender} {hero.score}\n")

    def step(self, obs):
        self.update(obs)
        if self.action:
            return self.action

        self.curBrain.execute_next(self.curLevel())
        return self.action
