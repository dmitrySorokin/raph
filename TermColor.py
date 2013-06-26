from myconstants import *

class TermColor:
    def __init__(self, fg=None, bg=None, bold=None, reverse=None):
        self.fg = fg or 37
        self.bg = bg or 0
        self.bold = bold or False
        self.reverse = reverse or False
    def getId(self):
        if self.fg == COLOR_YELLOW and not self.bold:
            return COLOR_BROWN
        if self.fg == COLOR_WHITE and not self.bold:
            return COLOR_GRAY
        if self.fg == COLOR_CYAN and self.bold:
            return COLOR_BRIGHT_CYAN
        if self.fg == COLOR_BLUE and self.bold:
            return COLOR_BRIGHT_BLUE
        if self.fg == COLOR_MAGENTA and self.bold:
            return COLOR_BRIGHT_MAGENTA
        if self.fg == COLOR_GREEN and self.bold:
            return COLOR_BRIGHT_GREEN
        return self.fg
    def copy(self):
        ret = TermColor(self.fg, self.bg, self.bold, self.reverse)
        return ret
    def __str__(self):
        return "fg:%s, bg:%s, b:%s, r:%s" % tuple(map(str, [self.fg, self.bg, self.bold, self.reverse]))
