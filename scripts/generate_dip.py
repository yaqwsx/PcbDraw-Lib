#!/usr/bin/env python

"""
Generates pin header in KiCAD style from a single pin model.
Models are generated in current working directory.
"""

from lxml import etree
from copy import deepcopy
import argparse 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", help="Single pin header model. Group with id 'pin' has to be present.");
    parser.add_argument("file_template", help="Python formatting string for name of the models.")

    args = parser.parse_args()
    
    for pins in [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32]:
        # Get the document's items
        document = etree.parse(args.model)
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
        # For all middle pins, copy the left and right one in the template and shift it down
        for i in range(1, (pins//2)-2):
            for p in range(1, 2+1):
                pin = root.find(".//*[@id='m-pin{}']".format(p))
                el = deepcopy(pin)
                del el.attrib["id"]
                el.attrib["transform"] = "translate(0 {})".format(i * 2.54)
                root.append(el)
        # Move the outside pin
        for p in range(1, 2+1):
            pin = root.find(".//*[@id='b-pin{}']".format(p))
            el = deepcopy(pin)
            del el.attrib["id"]
            el.attrib["transform"] = "translate(0 {})".format(((pins//2)-1) * 2.54)
            root.append(el)
        # Change the main body's lower dimension
        body.attrib["d"] = body.attrib["d"].replace("8.3819999", str((pins//2 * 2.54)-(0.02*25.4)))
        # Add back the body, dot, and origin to the SVG file to lay them on top of the pins
        root.append(body)
        root.append(first_pin_dot)
        root.append(origin)
        # Export the document
        document.write(args.file_template.format(pins))
