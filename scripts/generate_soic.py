#!/usr/bin/env python

"""
Generates pin header in KiCAD style from a single pin model.
Models are generated in current working directory.
"""
import os
from lxml import etree
from copy import deepcopy
import argparse

corner_rad = 0.3

# TODO: width settings does nothing right now
soic_settings = [
  {'pins': 8, 'width': 3.9, 'height': 4.9},
  {'pins': 8, 'width': 5.3, 'height': 5.3},
  {'pins': 8, 'width': 5.23, 'height': 5.23},
  {'pins': 14, 'width': 3.9, 'height': 8.7},
  {'pins': 16, 'width': 3.9, 'height': 9.9},
]

if __name__ == "__main__":
    for soic in soic_settings:
        # Get the document's items
        document = etree.parse('base/SOIC.svg')
        root = document.getroot()

        # Delete all inkscape grids
        p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
        for c in p.findall("{http://www.inkscape.org/namespaces/inkscape}grid"):
            p.remove(c)

        origin = root.find(".//*[@id='origin']")
        body = root.find(".//*[@id='body_path']")
        first_pin_dot = root.find(".//*[@id='first_pin_dot']")
        # Remove the origin, body, and first dot pin to add later
        # This is to place them above the pins
        root.remove(origin)
        root.remove(body)
        root.remove(first_pin_dot)
        sh = soic['height']
        sw = soic['width']
        # Copy the pin and use that to make other pins
        pin_copy = root.find(".//*[@id='pin']")
        root.remove(pin_copy)
        for r in [-1, 1]:
            for c in range(1, soic['pins']//2+1):
                el = deepcopy(pin_copy)
                del el.attrib["id"]
                el.attrib["y"] = "{}".format((soic['pins']/4-c)* 1.27 - 0.2 + 1.27/2)
                el.attrib["x"] = "{}".format(r*(sw/2 + 0.5) - 0.5)
                root.append(el)
        # Change the main body's lower dimension
        body.attrib["d"] = "m {},{} h {} c 0,0 0.3,0 0.3,0.3 l 0,{} c 0,0.3 -0.3,0.3 -0.3,0.3 h {} c 0,0 -0.3,0 -0.3,-0.3 l 0,{} c 0,-0.3 0.3,-0.3 0.3,-0.3 z".format(corner_rad-sw/2, -sh/2, sw-corner_rad*2, sh-corner_rad*2, -(sw-corner_rad*2), -(sh-corner_rad*2))
        # Move the dot
        first_pin_dot.attrib["cy"] = str(-((sh/2) - 0.8))
        first_pin_dot.attrib["cx"] = str(-((sw/2) - 0.8))
        # Add back the body, dot, and origin to the SVG file to lay them on top of the pins
        root.append(body)
        root.append(first_pin_dot)
        root.append(origin)
        # Export the document
        sn = "export/SOIC-{}_{:.2f}x{:.2f}mm_P1.27mm.svg".format(soic['pins'], sw, sh)
        if not os.path.isdir("export"):
          os.mkdir("export")
        document.write(sn)
        os.system(f"inkscape {sn} -D -o {sn} ;")
