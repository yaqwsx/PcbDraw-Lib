#!/usr/bin/env python

"""

This script is to be ran inside KiCAD-base/Resistor_THT

The base design's resistor is 6.0 x 2.075mm, so a new resistor lenght and width must be 
scaled from this size to the desired size.
"""

from lxml import etree
from copy import deepcopy
import os

res_options = [
  {'din': 'DIN0204', 'l': 3.6, 'd': 1.6, 'ps': [5.08, 7.62]},
  {'din': 'DIN0207', 'l': 6.3, 'd': 2.5, 'ps': [7.62, 10.16, 15.24]},
  {'din': 'DIN0309', 'l': 9.0, 'd': 3.2, 'ps': [12.7, 15.24, 20.32, 25.4]},
  {'din': 'DIN0411','l': 9.9, 'd': 3.6, 'ps': [12.7, 15.24, 20.32, 25.4]},
  {'din': 'DIN0414','l': 11.9, 'd': 4.5, 'ps': [15.24, 20.32, 25.4]},
  #{'din': 'DIN0516','l': 15.5, 'd': 5.0, 'ps': [20.32, 25.4, 30.48]},
  #{'din': 'DIN0614','l': 14.3, 'd': 5.7, 'ps': [15.24, 20.32, 25.4]},
  #{'din': 'DIN0617','l': 17.0, 'd': 6.0, 'ps': [20.32, 25.4, 30.48]},
  #{'din': 'DIN0918','l': 18.0, 'd': 9.0, 'ps': [22.86, 25.4, 30.48]},
  #{'din': 'DIN0922','l': 20.0, 'd': 9.0, 'ps': [25.4, 30.48]},
]

def map_scale(old_scale, new_scale):
    # Assume a zero old and new min value
    return new_scale / old_scale

def map_stroke_value(s_v, old_scale, new_scale):
    return s_v / new_scale * old_scale

if __name__ == "__main__":
    if not os.path.isdir("export"):
      os.mkdir("export")
      
    for r in res_options:
        for pin_len in r['ps']:
            document = etree.parse("base/R_Axial_Horizonal_BASE.svg")
            root = document.getroot()
            
            # Delete all inkscape grids
            p = root.find("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview")
            for c in p.findall("{http://www.inkscape.org/namespaces/inkscape}grid"):
                p.remove(c)
            
            # Remove the origin to add later. This is to place them above the pins
            origin = root.find(".//*[@id='origin']")
            root.remove(origin)
            
            # Change the pin's lenght to the one for a particular resistor
            pin = root.find(".//*[@id='main_pin']")
            pin.attrib["d"] = pin.attrib["d"].replace("10", str(pin_len))
            
            # Find the main body, then transform it
            bean = root.find(".//*[@id='res_bean']")
            bean.attrib["transform"] = "translate({}, 0) scale({}, {})".format((pin_len/2)-(r['l']/2), map_scale(6.0, r['l']), map_scale(2.075, r['d']))
            
            bean_outline = root.find(".//*[@id='bean_outline']")
            bean_outline.attrib["style"] = bean_outline.attrib["style"].replace("0.0900001", str(map_stroke_value(0.0900001, 6.0, r['l'])))
            
            # Add the origin back
            root.append(origin)
            # Save
            document.write("export/R_Axial_{:}_L{:.1f}mm_D{:.1f}mm_P{:.2f}mm_Horizontal.svg".format(r['din'], r['l'], r['d'], pin_len))
