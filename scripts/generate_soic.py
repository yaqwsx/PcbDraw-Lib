#!/usr/bin/env python

"""
Generates pin header in KiCAD style from a single pin model.
Models are generated in current working directory.
"""
import os
from lxml import etree
from copy import deepcopy
import argparse 

soic_height = {
  8: 4.9,
  14: 8.7,
  16: 9.9,
}
soic_body_width = 3.9
lead_width = 1.0
corner_rad = 0.3

if __name__ == "__main__":    
    for pins in [8, 14, 16]:
        # Get the document's items
        document = etree.parse('base/SOIC_W3.9.svg')
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
        # Move pins up and down
        for i in range(1, pins//4):
            for l_r in ['l', 'r']:
                for u_p in ['u', 'd']:
                    pin = root.find(".//*[@id='{}-{}-pin']".format(l_r, u_p))
                    el = deepcopy(pin)
                    del el.attrib["id"]
                    if u_p == 'u':
                      el.attrib["transform"] = "translate(0 {})".format(-i * 1.27)
                    else:
                      el.attrib["transform"] = "translate(0 {})".format(i * 1.27)
                    root.append(el)
        # Change the main body's lower dimension
        sh = soic_height[pins]
        body.attrib["d"] = "m {},{} h 3.3 c 0,0 0.3,0 0.3,0.3 l 0,{} c 0,0.3 -0.3,0.3 -0.3,0.3 h -3.3 c 0,0 -0.3,0 -0.3,-0.3 l 0,{} c 0,-0.3 0.3,-0.3 0.3,-0.3 z".format(corner_rad-soic_body_width/2, -sh/2, sh-corner_rad*2, -(sh-corner_rad*2))
        # Move the dot
        first_pin_dot.attrib["cy"] = str(-((sh/2) - 0.8))
        first_pin_dot.attrib["cx"] = str(-((soic_body_width/2) - 0.8))
        # Add back the body, dot, and origin to the SVG file to lay them on top of the pins
        root.append(body)
        root.append(first_pin_dot)
        root.append(origin)
        # Export the document
        sn = "export/SOIC_{}.svg".format(pins)
        if not os.path.isdir("export"):
          os.mkdir("export")
        document.write(sn)
        os.system(f"inkscape {sn} -D -o {sn} ;")
