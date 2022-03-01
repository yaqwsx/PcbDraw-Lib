#!/usr/bin/env bash
for i in `find . -name '*.svg'`; do
  if [[ " ./$@ " =~ " $i " ]]; then
    continue
  fi
  echo "Processing $i"; 
  inkscape $i -D -o $i ; 
done
