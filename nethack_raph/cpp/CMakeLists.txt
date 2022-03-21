cmake_minimum_required(VERSION 3.9)

project(algo VERSION 0.0.1)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE RELEASE)

if (${CMAKE_SYSTEM_NAME} STREQUAL Windows)
    add_definitions(-DBUILDING_FOR_WINDOWS -D_USE_MATH_DEFINES)
endif()

add_library(algo SHARED src/algo.cpp)

set_target_properties(algo PROPERTIES PUBLIC_HEADER include/algo.h)

target_include_directories(algo PRIVATE include)

install(TARGETS algo
    DESTINATION ${CMAKE_INSTALL_PREFIX}
    PUBLIC_HEADER DESTINATION include)
