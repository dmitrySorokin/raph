#!/bin/bash

cd /tmp
find . -maxdepth 1 -name "nethack.Agent.*" -print0 | xargs -0 rm
#rm -rf /tmp/nethack.Agent.*
rm -rf poly*
rm -rf nle*

pkill -f polyhydra.py
