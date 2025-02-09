#!/usr/bin/env bash
for i in `find . -name '*.svg'`; do
  if [[ !($@ -ef `dirname $i`) ]]; then
    echo "Skipping $i";
    continue
  fi
  echo "Processing $i";
  inkscape $i -D -o $i;
done
