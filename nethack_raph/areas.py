import numpy

from collections import deque

from nle.nethack import glyph_is_cmap

from nle.nethack import (
    GLYPH_MON_OFF,      # a monster
    GLYPH_PET_OFF,      # a pet
    GLYPH_INVIS_OFF,    # invisible
    GLYPH_DETECT_OFF,   # mon detect
    GLYPH_BODY_OFF,     # a corpse
    GLYPH_RIDDEN_OFF,   # mon ridden
    GLYPH_OBJ_OFF,      # object
    GLYPH_CMAP_OFF,     # cmap
    GLYPH_EXPLODE_OFF,  # explosion
    GLYPH_ZAP_OFF,      # zap beam
    GLYPH_SWALLOW_OFF,  # swallow
    GLYPH_WARNING_OFF,  # warn flash
    GLYPH_STATUE_OFF,   # a statue
    MAX_GLYPH,          # (end)
)


class ScreenSymbol:
    """Copied verbatim from include/rm.h"""
    # /* begin dungeon characters */
    S_stone     =  0
    S_vwall     =  1
    S_hwall     =  2
    S_tlcorn    =  3
    S_trcorn    =  4
    S_blcorn    =  5
    S_brcorn    =  6
    S_crwall    =  7
    S_tuwall    =  8
    S_tdwall    =  9
    S_tlwall    = 10
    S_trwall    = 11
    S_ndoor     = 12
    S_vodoor    = 13
    S_hodoor    = 14
    S_vcdoor    = 15  # /* closed door, vertical wall */
    S_hcdoor    = 16  # /* closed door, horizontal wall */
    S_bars      = 17  # /* KMH -- iron bars */
    S_tree      = 18  # /* KMH */
    S_room      = 19
    S_darkroom  = 20
    S_corr      = 21
    S_litcorr   = 22
    S_upstair   = 23
    S_dnstair   = 24
    S_upladder  = 25
    S_dnladder  = 26
    S_altar     = 27
    S_grave     = 28
    S_throne    = 29
    S_sink      = 30
    S_fountain  = 31
    S_pool      = 32
    S_ice       = 33
    S_lava      = 34
    S_vodbridge = 35
    S_hodbridge = 36
    S_vcdbridge = 37  # /* closed drawbridge, vertical wall */
    S_hcdbridge = 38  # /* closed drawbridge, horizontal wall */
    S_air       = 39
    S_cloud     = 40
    S_water     = 41

    #  /* end dungeon characters, begin traps */
    pass  # omitted

    #  /* end traps, begin special effects */
    pass  # omitted

    #  /* The 8 swallow symbols.  Do NOT separate.  To change order or add, */
    #  /* see the function swallow_to_glyph() in display.c.                 */
    S_sw_tl     = 79  #  /* swallow top left [1]             */
    S_sw_tc     = 80  #  /* swallow top center [2]    Order: */
    S_sw_tr     = 81  #  /* swallow top right [3]            */
    S_sw_ml     = 82  #  /* swallow middle left [4]   1 2 3  */
    S_sw_mr     = 83  #  /* swallow middle right [6]  4 5 6  */
    S_sw_bl     = 84  #  /* swallow bottom left [7]   7 8 9  */
    S_sw_bc     = 85  #  /* swallow bottom center [8]        */
    S_sw_br     = 86  #  /* swallow bottom right [9]         */

    pass  # omitted

    #  /* end effects */
    MAXPCHARS   = 96  #  /* maximum number of mapped characters */


# manually determined based on close inspection of rm.h and display.h
glyph_is_floodable = {
    # *range(GLYPH_BODY_OFF, GLYPH_RIDDEN_OFF),  # all corpses
    # *range(GLYPH_OBJ_OFF, GLYPH_CMAP_OFF),     # all objects

    GLYPH_CMAP_OFF + ScreenSymbol.S_room,
    GLYPH_CMAP_OFF + ScreenSymbol.S_darkroom,

    # an empty doorway is like a floor
    # GLYPH_CMAP_OFF + ScreenSymbol.S_ndoor,

    GLYPH_CMAP_OFF + ScreenSymbol.S_upstair,
    GLYPH_CMAP_OFF + ScreenSymbol.S_dnstair,
    GLYPH_CMAP_OFF + ScreenSymbol.S_upladder,
    GLYPH_CMAP_OFF + ScreenSymbol.S_dnladder,
    GLYPH_CMAP_OFF + ScreenSymbol.S_altar,
    GLYPH_CMAP_OFF + ScreenSymbol.S_grave,
    GLYPH_CMAP_OFF + ScreenSymbol.S_throne,
    GLYPH_CMAP_OFF + ScreenSymbol.S_sink,
    GLYPH_CMAP_OFF + ScreenSymbol.S_fountain,
    GLYPH_CMAP_OFF + ScreenSymbol.S_pool,

    # if we're swallowed, then treat the belly as a room
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_tl,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_tc,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_tr,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_ml,
    # NB no middle-middle
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_mr,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_bl,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_bc,
    GLYPH_SWALLOW_OFF + ScreenSymbol.S_sw_br,

    *range(GLYPH_STATUE_OFF, MAX_GLYPH),   # all statues
}


class UnionFind:
    """A two-pass implementation of the union find."""
    _parent = None  # autolink to self

    def __bool__(self):
        return self._parent is None

    def link(self, parent):
        self._parent = None if parent is self else parent

    @property
    def parent(self):
        # find the root until we hit a loop placeholder
        root = self
        while root._parent is not None:
            root = root._parent

        # no need to do anything if we're looping
        if self._parent is None:
            return self

        # ascend for the second time
        while self._parent is not root:
            self, self._parent = self._parent, root

        return root


class Area(UnionFind):
    """A flood filled area."""

    def __init__(self, area_id, map):
        self.area_id = area_id
        self.mask = map == area_id

        # get a crude bounding rect (top-left, bot-right)
        x, y = self.mask.nonzero()
        self.rect = (x.min(), y.min()), (x.max(), y.max())

    def __contains__(self, xy):
        # delegate to the parent area if we have been merged
        return self.parent.mask[xy]

    def __repr__(self):
        return f"Area({self.area_id:d}) :: {self.mask.sum()}"

    def render(self, rect=False):
        self = self.parent

        ansi = ''
        if rect:
            (t, l), (b, r) = self.rect
            xy = list(zip(*[(x, y) for x in range(t, b+1) for y in range(l, r+1)]))
            # breakpoint()
        else:
            xy = self.mask.nonzero()

        for r, c in zip(*xy):
            ansi += f'\x1b[6;31m\x1b[{r+2};{c+1}H{self.area_id&15:1X}\x1b[m'

        return ansi


def flood(pool, glyphs, map, at, *, floodable=glyph_is_floodable):
    """Simple lazy flood filler on glyphs.
    """
    assert map.shape == glyphs.shape

    # cannot flood anything
    if glyphs[at] not in floodable:
        return None

    # refuse to initiate filling from already flooded areas
    if map[at] >= 0:
        # if we ever request a flood-fill that results in filling a connecting
        #  area from "wilderness", then the areas will be merged and its id
        #  overwrittern.
        return pool[map[at]]

    # allocate new id in the managed pool of areas (dict)
    value = 1 + max(pool.keys(), default=-1)

    # bfs tracks `visitation` at the point of enqueuing adjacent nodes. Cannot
    # reuse `map` for this, since it is updated out of sync with the frontier.
    visited = numpy.zeros(map.shape, dtype=bool)

    # flood fill with the new value, optionally spilling over
    #  to connecting areas filled previously.
    frontier, merged, n_cells = deque([at]), set(), 0
    visited[at] = True

    h, w = glyphs.shape
    while frontier:
        r, c = frontier.popleft()
        if glyphs[r, c] not in floodable:
            continue

        # make sure to fill the center before inspecting the neighbours
        map[r, c] = value
        n_cells += 1

        # assume that floodable glyphs are always away from the border
        # XXX this seems quite slow, but we resort to here rarely.
        for rr in r-1, r, r+1:
            assert 0 <= rr < h
            for cc in c-1, c, c+1:
                assert 0 <= cc < w
                # fill wilderness (-1) and spillover to touching areas (>= 0)
                if map[rr, cc] != value and not visited[rr, cc]:
                    frontier.append((rr, cc))
                    visited[rr, cc] = True

                    # remember the merged areas
                    if map[rr, cc] >= 0:
                        merged.add(map[rr, cc])

    # the new area has captured the adjacent areas, so we just link them,
    #  since other users may keep references to the merged areas.
    parent = pool[value] = Area(value, map)
    for area in merged:
        pool[area].link(parent)

    return parent
