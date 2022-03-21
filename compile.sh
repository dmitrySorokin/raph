#!/usr/bin/env bash

cd nethack_raph/cpp
pwd

# clean-up cpp
rm -rf build

# compile & install cpp
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=../../libs/ ../
make install -j7

