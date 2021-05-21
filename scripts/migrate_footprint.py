#!/usr/bin/env python3

import sys
from lxml import etree

"""
The library convention for units have changed since PcbDraw v0.6. This scripts
migrates the old-style libraries into the new unit format.

Usage: ./migrate_library.py footprint.svg
"""

def run():
    tree = etree.parse(sys.argv[1])
    root = tree.getroot()
    x, y, w, h = root.attrib["viewBox"].split()
    root.attrib["width"] = f"{w}mm"
    root.attrib["height"] = f"{h}mm"

    tree.write(sys.argv[1])

if __name__ == "__main__":
    run()