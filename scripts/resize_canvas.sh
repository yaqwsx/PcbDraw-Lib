#!/usr/bin/env bash

for i in `find . -name '*.svg'`; do echo "Processing $i"; inkscape $i -D -o $i ; done
