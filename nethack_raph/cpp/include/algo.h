#pragma once

#include <cstdint>

extern "C" {
	void dijkstra(double* walk_costs, int32_t source, bool* targets, int32_t* path, bool* doors);
}

