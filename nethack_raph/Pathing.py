import numpy as np
from math import isfinite

from heapq import heappop, heappush
from collections import defaultdict
from ctypes import *
import os
import platform

from nethack_raph.myconstants import DUNGEON_WIDTH, DUNGEON_HEIGHT

def calc_corner_adjacent():
    offsets = {(-1, -1), (-1, 1), (1, -1), (1, 1)}
    result = []
    for x in range(DUNGEON_HEIGHT):
        for y in range(DUNGEON_WIDTH):
            neibs = []
            for h, w in offsets:
                if x + h >= DUNGEON_HEIGHT: continue
                if x + h < 0: continue
                if y + w >= DUNGEON_WIDTH: continue
                if y + w < 0: continue
                neibs.append((x + h) * DUNGEON_WIDTH + y + w)
            result.append(tuple(neibs))
    return result

def calc_edge_adjacent():
    offsets = {(-1, 0), (0, -1), (0, 1), (1, 0)}
    result = []
    for x in range(DUNGEON_HEIGHT):
        for y in range(DUNGEON_WIDTH):
            neibs = []
            for h, w in offsets:
                if x + h >= DUNGEON_HEIGHT: continue
                if x + h < 0: continue
                if y + w >= DUNGEON_WIDTH: continue
                if y + w < 0: continue
                neibs.append((x + h) * DUNGEON_WIDTH + y + w)
            result.append(tuple(neibs))
    return result

_CORNER_ADJACENT = calc_corner_adjacent()
_EDGE_ADJACENT = calc_edge_adjacent()


class Node:
    __slots__ = 'xy', 'cost'

    def __init__(self, xy, cost):
        self.xy = xy
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __hash__(self):
        return self.xy

    def __eq__(self, other):
        return self.xy == other.xy


def reconstruct_path(prev, goal):
    result = []
    while goal is not None:
        result.append(divmod(goal.xy, DUNGEON_WIDTH))
        goal = prev[goal]
    return result


def dijkstra_py(walk_costs, start, mask, doors):
    walk_costs = walk_costs.reshape(-1)
    coords = mask.reshape(-1)
    doors = doors.reshape(-1)
    start = int(start[0] * DUNGEON_WIDTH + start[1])

    def neighbours_gen(xy, doors):
        for neib in _EDGE_ADJACENT[xy]:
            yield neib
        if not doors[xy]:
            for neib in _CORNER_ADJACENT[xy]:
                if not doors[neib]:
                    yield neib

    cost = defaultdict(lambda: float('inf'))
    prev = {}

    # init start
    node = Node(start, 0)
    frontier = [node]
    cost[node] = 0.
    prev[node] = None

    # run dijkstra with premature termination
    while frontier:
        current = heappop(frontier)

        if coords[current.xy]:
            return reconstruct_path(prev, current)

        # no need to re-inspect stale heap records
        if cost[current] < current.cost:
            continue

        # edge adjacent
        for neighbour in neighbours_gen(current.xy, doors):
            # consider tiles with finite +ve costs only
            walk_cost = walk_costs[neighbour]
            if isfinite(walk_cost) and walk_cost >= 0:

                node = Node(neighbour, cost[current] + walk_cost)
                if node.cost < cost[node]:
                    heappush(frontier, node)

                    cost[node] = node.cost
                    prev[node] = current

    return None


def check_neighbours(xy, coords):
    return coords[np.array(_EDGE_ADJACENT[xy])].any() or coords[np.array(_CORNER_ADJACENT[xy])].any()


def lib_path():
    dirname = os.path.dirname(__file__)

    system = platform.system()
    if system == 'Windows':
        lib_name = 'algo.dll'
    elif system == 'Darwin':
        lib_name = 'libalgo.dylib'
    else:
        lib_name = 'libalgo.so'

    return os.path.join(dirname, 'libs/' + lib_name)


libc = cdll.LoadLibrary(lib_path())
libc.dijkstra.argtypes = [
    POINTER(c_double),
    c_int32,
    POINTER(c_bool),
    POINTER(c_int32),
    POINTER(c_bool)
]


def dijkstra_cpp(walk_costs, start, targets_mask, doors):

    def to_pointer(nparray, dtype):
        return nparray.ctypes.data_as(POINTER(dtype))

    walk_costs = walk_costs.reshape(-1)
    targets_mask = targets_mask.reshape(-1).astype(np.bool)
    doors = doors.reshape(-1).astype(np.bool)
    start = int(start[0] * DUNGEON_WIDTH + start[1])

    path = np.full((2 * DUNGEON_WIDTH * DUNGEON_HEIGHT), -1, dtype=np.int32)
    libc.dijkstra(
        to_pointer(walk_costs, c_double),
        start,
        to_pointer(targets_mask, c_bool),
        to_pointer(path, c_int32),
        to_pointer(doors, c_bool)
    )
    path = path[np.where(path != -1)]
    path = path.reshape((-1, 2))
    path = list(map(tuple, path))

    return path if path else None
