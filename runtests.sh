#!/bin/sh
set -e
0launch http://gfxmonk.net/dist/0install/0local.xml python-pea.xml
0launch --command=test python-pea-local.xml -v
