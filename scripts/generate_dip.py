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
    
    for pins in [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32]:
        document = etree.parse(args.model)
        root = document.getroot()
        origin = root.find(".//*[@id='origin']")
        body = root.find(".//*[@id='body_path']")
        first_pin_dot = root.find(".//*[@id='first_pin_dot']")
        root.remove(origin)
        root.remove(body)
        root.remove(first_pin_dot)
        for i in range(pins//2):
          for p in range(1, 3):
            pin = root.find(".//*[@id='pin{}']".format(p))
            el = deepcopy(pin)
            del el.attrib["id"]
            el.attrib["transform"] += " translate({} 0)".format(i * 2.54)
            root.append(el)
        
        body.attrib["d"] = body.attrib["d"].replace("FILL_HERE", str((pins//2) * 2.54))
        
        root.append(body)
        root.append(first_pin_dot)
        root.append(origin)
        document.write(args.file_template.format(pins))
