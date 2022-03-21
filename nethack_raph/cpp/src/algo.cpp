#include "algo.h"

#include <vector>
#include <algorithm>
#include <iostream>
#include <queue>
#include <climits>
#include <cmath>
#include <tuple>

constexpr int DUNGEON_WIDTH = 79;
constexpr int DUNGEON_HEIGHT = 21;
constexpr int MAX_NODE = DUNGEON_WIDTH * DUNGEON_HEIGHT;

namespace {

struct Node {
    int32_t id;
    double cost;
};

bool operator > (const Node& left, const Node& right) {
    return left.cost > right.cost;
}

void reconstruct_path(int32_t* came_from, int32_t source, int32_t target, int32_t* path) {
    int current = target;
    int i = 0;
    path[i] = current / DUNGEON_WIDTH;
    path[i + 1] = current % DUNGEON_WIDTH;
    i += 2;
    while (current != source) {
        current = came_from[current];
        path[i] = current / DUNGEON_WIDTH;
        path[i + 1] = current % DUNGEON_WIDTH;
        i += 2;
    }
}

} // namespace


void dijkstra(double* walk_costs, int32_t source, bool* targets, int32_t* path, bool* doors)
{
    static const std::vector<std::tuple<int, int, bool>> offsets = {
        {-1, -1, true}, {-1, 1, true}, {1, -1, true}, {1, 1, true},
        {-1, 0, false}, {0, -1, false}, {0, 1, false}, {1, 0, false}
    };

    int came_from[MAX_NODE];
    std::vector<double> cost_so_far(MAX_NODE, LLONG_MAX);
    std::priority_queue<Node, std::vector<Node>, std::greater<Node>> queue;
    queue.push({source, 0});
    cost_so_far[source] = 0;
    while (!queue.empty()) {
        auto [current, cost] = queue.top();
        queue.pop();
        if (targets[current]) {
            reconstruct_path(came_from, source, current, path);
            return;
        }

        int i = current / DUNGEON_WIDTH;
        int j = current % DUNGEON_WIDTH;
        for (auto [delta_i, delta_j, is_corner] : offsets) {
            int neigh_i = i + delta_i;
            int neigh_j = j + delta_j;
            if (neigh_i < 0 || neigh_i >= DUNGEON_HEIGHT || neigh_j < 0 || neigh_j >= DUNGEON_WIDTH) {
                continue;
            }
            int neighbour = neigh_i * DUNGEON_WIDTH + neigh_j;

            if (is_corner && (doors[neighbour] || doors[current])) {
                continue;
            }

            if (std::isinf(walk_costs[neighbour])) {
                continue;
            }
            double neighbour_cost = cost_so_far[current] + walk_costs[neighbour];
            if (neighbour_cost < cost_so_far[neighbour]) {
                cost_so_far[neighbour] = neighbour_cost;
                queue.push({neighbour, neighbour_cost});
                came_from[neighbour] = current;
            }
        }
    }
}
